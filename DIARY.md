# Data Diary for OATH Database
----
### Nov 30

- Downloaded exported data from NYC open data
- Started pulling cases and made dynamic pages by using the case route, just chose some really basic info to start
- Made dynamic pages for the 'Issuing Agency' field 
- Changed a bunch of names of columns in the SQL database to be underscores -- probably shouldn't do this manually in the future
- Things are running super slow...probably need to use SQL instead of loading the CSV in directly
- Changed over to a SQLite database since I think that'll be faster and better for later

Note for future: This data is SO messy. Different departments using different methods for filling in each case, and many departments that may use different naming conventions, even to reference themselves. 


### Dec 2

- Added index columns for ticket number and department to attempt to speed up querying times.
    - Loading the intiial page got a lot faster, but the not the loading of department pages. 
- Added plotly graphs for sum of total fines over time and cases
- Added pagination with the help of chatgpt and claude https://claude.ai/chat/d4c8ba89-07bd-4a88-bfe1-68407311cf62


# Dec 5

- Focused a bunch on styling the home page, case pages and department pages
- Added a home page navigation bar

# Dec 7

- Changed department to a dropdown list

- Added text search for code violation, had to make sure that I was only searching words since it would get depARTment when searching for 'art'

- Changed search and department HTML pages into one HTML page called aggregate.html

### Dec 9

- Added a bunch more to the case page, including a link to the actual summons if it exists. The URL is standardized, so it's a pretty easy paste to get the URL
    - Also added other violations aside from the primary one using a plotly table

### Dec 10

- Added most common case descriptions to get an idea of what a search or department was actually fining people for

# Dec 13

- Made pagination better using Soma's new method + some GPTing
- Narrowed down the SQLite database to a smaller file so I can push to GitHub without issue -- ideally I'd want to host this somewhere I think
- Changed line charts from plotly to bar charts