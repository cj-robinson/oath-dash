from flask import Flask, render_template, request
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import plotly.express as px

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
    # case_count = f"{oath_cases.query.count():,}"
    # oath_case_sample = oath_cases.query.filter(oath_cases.violation_details != "").limit(10)
    
    # month_count = oath_cases.query.with_entities(
    # func.strftime('%Y-%m', oath_cases.violation_date_formatted).label('month'),
    # func.count().label('count'))

    
    # count_fig = px.line(x=[row.month for row in month_count], y=[row.count for row in month_count], title='Cases Filed', labels={'x': 'Month', 'y': 'Cases'})
    # count_graph_json  = count_fig.to_json()

    # Pagination parameters
    page = request.args.get("page", 1, type=int)  # Default to page 1
    per_page = request.args.get("per_page", 10, type=int)  # Default to 10 items per page

    # Total number of distinct departments
    total_departments = (
        oath_cases.query
        .filter(oath_cases.issuing_agency != "")
        .with_entities(oath_cases.issuing_agency)
        .distinct()
        .count()
    )

    # Calculate offset for pagination
    offset = (page - 1) * per_page

    # Fetch paginated department list
    dept_list_query = (
        oath_cases.query
        .filter(oath_cases.issuing_agency != "")
        .with_entities(oath_cases.issuing_agency)
        .distinct()
        .offset(offset)
        .limit(per_page)
    )

    dept_list = [department[0] for department in dept_list_query]

    # Calculate total pages
    total_pages = (total_departments + per_page - 1) // per_page  # Round up for partial pages

    # Render template with pagination data
    return render_template(
        'oath.html',
        # case_count=case_count,
        # oath_case_sample=oath_case_sample,
        dept_list=dept_list,
        current_page=page,
        total_pages=total_pages,
        # count_graph_json=count_graph_json
    )
    
@app.route("/case/<string:case_id>")
def case_page(case_id):
    case = oath_cases.query.filter_by(ticket_number = case_id).first()

    return render_template(
        'case.html',
        case=case
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

    case_list = list(set(df['ticket_number']))
    case_count = f"{len(case_list):,}"
    # change to a date
    df['month'] = pd.to_datetime(df['violation_date_formatted']).dt.month

    # change to float
    df['total_violation_amount'] = df['total_violation_amount'].astype(float, errors='ignore')

    # get count by month
    month_count = df.groupby(df['month']).agg({
        'total_violation_amount':['sum','count']
    })

    top_10_codes = df['Charge #1: Code Description'].value_counts().sort_values(ascending = False).head(10).sort_values()

    month_count.columns = ['sum', 'count']  # Flatten column names
    
    count_fig = px.line(x=month_count.index, y=month_count['count'], title='Cases Filed', labels={'x': 'Month', 'y': 'Cases'})
    count_graph_json  = count_fig.to_json()

    sum_fig = px.line(x=month_count.index, y=month_count['sum'], title='Sum of Total Violation Fines', labels={'x': 'Month', 'y': '$'})
    sum_graph_json  = sum_fig.to_json()
    
    top_10_fig = px.bar(x=top_10_codes.values, y=top_10_codes.keys(), title='Top Code Descriptions', labels={'x': 'Number of Violations', 'y': 'Code Description'})
    
    # Update the layout to ensure the labels fit
    top_10_fig.update_layout(
        yaxis=dict(
            tickangle=0,  # Rotate labels slightly if needed, or try 90 for vertical
            automargin=True  # Automatically adjust the margin for longer labels
        ),
        margin=dict(t=40, b=80)  # Adjust the top and bottom margins to allow for longer labels
    )

    top_10_graph_json  = top_10_fig.to_json()

    return render_template(
        'dept.html',
        case_count=case_count,
        dept_name=dept_name,
        count_graph_json=count_graph_json,
        sum_graph_json=sum_graph_json,
        top_10_graph_json=top_10_graph_json,
        case_list=case_list
    )