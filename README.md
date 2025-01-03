# OATH Dashboard

Find the live site here: https://oath-dash.onrender.com/

Overview
--
This repository contains data for an exploratory Flask app to understand data from the [Office of Adminstration Trials and Hearings (OATH)](https://www.nyc.gov/site/oath/index.page). It is pulled from [NYC Open Data](https://data.cityofnewyork.us/City-Government/OATH-Hearings-Division-Case-Status/jz4z-kudi/about_data), and for the purposes of exploration, only has a small sample of data.  The app uses dynamic routing to explore individual cases, departments or searches of terms in code violations. 

Goals
--
The OATH Dashboard was created as a final project for Foundations in Computing, Fall 2024 for the Data Journalism program at Columbia Journalism School. In this course, we focus on (mostly) Python-based data exploration through things like command line tools, pandas, OCR, Selenium/web scraping and GIS. We had several options for a final project, one of which was building a web-based front end for a large dataset. I chose to use the OATH data as I was interested in trends in NYC Sheriff enforcement of illegal cannabis stores in NYC and wanted to find other interesting cases and trends. The dataset is largely inaccessible to those without data skills due to its size. 

Process
--
I chose a Flask app since it's a fairly reliable way of templatizing pages for multiple subsections of data or indiviudal data points. I began with creating a basic page for each case (represented by a single row in the dataset), then building out pages that give some trend information for each issuing agency with dynamic charts and paginated links to cases. I also added a similar page but for word-based text searches in the case description.

Find a more thorough explanation of my process in the data diary Markdown file. 

Learnings
--
This was my first time working in Flask and building out HTML pages from scratch. I found designing pages that looked presentable took a lot more time and effort than I expected with a blank HTML file in front of me. Since this was also a large dataset, I had to use a few different back-end services (starting with just a CSV and using pandas, then going to a SQLite database, then deciding to just upload a small sample to GitHub) to actually load and interact with the data. I'm interested in learning more about back-end dev and empowering users to find data through open-source APIs like  NYC Open Data though!
