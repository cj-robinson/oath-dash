from flask import Flask, render_template, request
from flask_paginate import Pagination, get_page_parameter
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import plotly.express as px
import plotly.graph_objects as go

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/cjrobinson/data/columbia/foundations/oath-dash/oath_database.sqlite'
db = SQLAlchemy(app)

with app.app_context():
    db.Model.metadata.reflect(db.engine)

class oath_cases(db.Model):
    __tablename__ = 'oath_jan_nov_2024'
    __table_args__ = { 'extend_existing': True }
    ticket_number = db.Column(db.Text, primary_key=True)

@app.route("/")
def home_page():
    #grab distinct departments
    dept_list_query = (
        oath_cases.query
        .filter(oath_cases.issuing_agency != "")
        .with_entities(oath_cases.issuing_agency)
        .distinct()
    )

    dept_list = [department[0] for department in dept_list_query]

    return render_template(
        'oath.html',
        dept_list=dept_list,

    )
    
@app.route("/case/<string:case_id>")
def case_page(case_id):
    case = oath_cases.query.filter_by(ticket_number = case_id).first()
    other_codes = {col: getattr(case, col) for col in case.__dict__ if col.startswith('Charge #')}
    other_codes = dict(sorted(other_codes.items(), key=lambda item: int(item[0].split('#')[1].split(':')[0])))
    # Create Plotly Table directly from the dictionary
    table = go.Figure(data=[
        go.Table(
            cells=dict(values=[list(other_codes.keys()), list(other_codes.values())], fill_color='lavender', align='left')
        )
    ])

    table_html = table.to_html(full_html=False)

    return render_template(
        'case.html',
        case=case,
        table_html=table_html
    )

@app.route("/department/<string:dept_name>")
def dept(dept_name):
    dept_name = dept_name.replace('-', ' ')
    cases = oath_cases.query.filter(func.lower(func.replace(oath_cases.issuing_agency, '-', ' ')) == dept_name.lower()).all()
    
    #chat gpt'd this to make the sql alch turn into a df
    data = [dict(case.__dict__) for case in cases]

    for row in data:
        row.pop('_sa_instance_state', None)  # Remove SQLAlchemy internal attribute
    
    df = pd.DataFrame(data)

    # pull individual cases via pagination
    case_list = list(set(df['ticket_number']))
    case_count = f"{len(case_list):,}"
    page = request.args.get(get_page_parameter(), type=int, default=1)

    PER_PAGE = 20
    current_page = int(request.args.get('page', 1)) 
    start = PER_PAGE * current_page - PER_PAGE
    end = PER_PAGE * current_page


    case_list = case_list[start:end]

    pagination = Pagination(page=page, 
                            total=df.shape[0],
                    current_page=current_page,
                    per_page=PER_PAGE) 

    # change to a date
    df['month'] = pd.to_datetime(df['violation_date_formatted']).dt.month

    # change to float
    df['total_violation_amount'] = pd.to_numeric(df['total_violation_amount'], errors='coerce')

    # get count by month
    month_count = df.groupby('month').agg({
        'total_violation_amount': 'sum',
        'ticket_number': 'count'  # Count the number of violations
    }).rename(columns={'total_violation_amount': 'sum', 'ticket_number': 'count'})
    
    count_fig = px.line(x=month_count.index, y=month_count['count'], title='Cases Filed', labels={'x': 'Month', 'y': 'Cases'})
    count_graph_json  = count_fig.to_json()

    sum_fig = px.line(x=month_count.index, y=month_count['sum'], title='Sum of Total Violation Fines', labels={'x': 'Month', 'y': '$'})
    sum_graph_json  = sum_fig.to_json()
    
    top_10_codes = df['charge_1_code_description'].value_counts().sort_values(ascending = False).head(10).sort_values(ascending=False)

    table = go.Figure(data=[go.Table(
        header=dict(values=["Case Description", "Count"], fill_color='paleturquoise', align='left'),
        cells=dict(values=[list(top_10_codes.keys()), list(top_10_codes.values)], fill_color='lavender', align='left')
    )])

    table_html = table.to_html(full_html=False)

    return render_template(
        'aggregate.html',
        case_count=case_count,
        title=dept_name,
        count_graph_json=count_graph_json,
        sum_graph_json=sum_graph_json,
        table_html=table_html,
        case_list=case_list,
        pagination=pagination,
        type="department"
    )

@app.route("/search/<string:search_text>")
def search(search_text):
    search_text = search_text.replace('-', ' ')
    # does a case sensitive search
    # Split the search_text into individual words
    words = search_text.lower().split()

    # Build a filter to search for cases containing all words
    filters = [
        oath_cases.charge_1_code_description.ilike(f'% {word} %') | 
        oath_cases.charge_1_code_description.ilike(f' {word} %') |
        oath_cases.charge_1_code_description.ilike(f'% {word}') 
        for word in words
    ]

    cases = oath_cases.query.filter(*filters).all()

    if not cases:
        case_count = 0
        return render_template(
            'aggregate.html',
            case_count=case_count,
            type="search"
        )
    else:
        #chat gpt'd this to make the sql alch turn into a df
        data = [dict(case.__dict__) for case in cases]

        for row in data:
            row.pop('_sa_instance_state', None)  # Remove SQLAlchemy internal attribute
        
        df = pd.DataFrame(data)

        # pull individual cases via pagination
        case_list = list(set(df['ticket_number']))
        case_count = f"{len(case_list):,}"
        page = request.args.get(get_page_parameter(), type=int, default=1)

        PER_PAGE = 20
        current_page = int(request.args.get('page', 1)) 
        start = PER_PAGE * current_page - PER_PAGE
        end = PER_PAGE * current_page


        case_list = case_list[start:end]

        pagination = Pagination(page=page, 
                                total=df.shape[0],
                        current_page=current_page,
                        per_page=PER_PAGE) 

        # change to a date
        df['month'] = pd.to_datetime(df['violation_date_formatted']).dt.month

        # change to float
        df['total_violation_amount'] = pd.to_numeric(df['total_violation_amount'], errors='coerce')

        # get count by month
        month_count = df.groupby('month').agg({
            'total_violation_amount': 'sum',
            'ticket_number': 'count'  # Count the number of violations
        }).rename(columns={'total_violation_amount': 'sum', 'ticket_number': 'count'})
        
        month_count.columns = ['sum', 'count']  # Flatten column names
        
        count_fig = px.line(x=month_count.index, y=month_count['count'], title='Cases Filed', labels={'x': 'Month', 'y': 'Cases'})
        count_graph_json  = count_fig.to_json()

        sum_fig = px.line(
            month_count, x=month_count.index, y='sum', title='Sum of Total Violation Fines',
            labels={'sum': 'Sum of Fines', 'x': 'Month'}
        )
        sum_graph_json  = sum_fig.to_json()
        
        top_10_codes = df['charge_1_code_description'].value_counts().sort_values(ascending = False).head(10).sort_values(ascending=False)

        table = go.Figure(data=[go.Table(
            header=dict(values=["Case Description", "Count"], fill_color='paleturquoise', align='left'),
        cells=dict(values=[list(top_10_codes.keys()), list(top_10_codes.values)], fill_color='lavender', align='left')
        )])

        table_html = table.to_html(full_html=False)

        return render_template(
            'aggregate.html',
            case_count=case_count,
            title=search_text,
            count_graph_json=count_graph_json,
            sum_graph_json=sum_graph_json,
            table_html=table_html,
            case_list=case_list,
            type="search",
            pagination=pagination
        )
