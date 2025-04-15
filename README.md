# Alpine Finance
This project is meant to be a new tool designed for security selection. Often times a security is selected as a result of meticulous analysis of a company. This will not change, however the meticulous analysis can often be sped up to spit out metrics on current data sets to determine whether the time required to go through a company is worth it. Security selection is not rocket science and it certainly does not need to be incredibly difficult. The easier this task can be the better it will be for us all.

This readme will be broken down into a couple section, each of which highlights some part of this project.

## Setup
Before being able to run anything, navigate to the root directory, and run the shell script to setup the repository. The shell script will:
* Put the alpine-finance package on the python path for directory navigation
* pip install -r requirements.txt

### DB system/Data Storage
- The database being used here is a postgres db
- It is hosted in a docker container and managed by django to orchestrate its existence
  - The database files can be found in the folder `postgres-data` in the `django_project` directory. Commits of data will persist there for now.  
  - Django directory is organised as though we were at Elfin Lakes
    - Upper Lake will contain the bulk of the data - this will serve as a catch-all kind-of a db
    - Lower Lake will contain a smaller amount of the data and will contain more processed data (ready for ML/NLP)
- The connection protocols (passwords and such) can be found in the .env file


## Data ETL 

### Data Ingestion
- The idea behind this folder is to ingest a pdf file and store it within a database system (psql instance for now hosted in a docker container) 
- A successful implementation of this project will include the following:
    * Data ingestion to a dockerized psql database
    * Data storage into the database under a storage scheme
    * Data that is ready to be ingested further in the future
    * All of this will be orchestrated with Django 
    * Option for ingestion of multiple files (single file path, a folder of files, drag and drop (?) feature)
    * Robust terminal output OR a GUI to help this
- Nice to haves:
    * GUI Features
    * Drag and Drop feature
    * Ability to orchestrate with Airflow for ingesting from an S3 bucket in the future (larger data ingestion stream)
* Data Flow:
  * In order to ingest this data from the SEC website, we need to 
    * Collect the tickers of all companies listed on various exchanges (EdgarQueryManager.security_data)
    * Collect all the filing urls for the last 20 years for each of these companies

### Data Transformation
- TBD: Basically need to convert the raw 10-k files into something more digestible for NLP
  - The data will go from the upper_lake to the lower_lake (like in real life)


### Machine Learning (Unsupervised Learning - DBSCAN)


### Ideal final use case:
1. Feed in a 10-K form (for US companies) - Eventually replicate to Canada and other markets around the world.
2. Convert this 100+ pages of text into a json blob that can be clustered to see similarities between similar 10-ks
3. Have the model spit back a set of metrics to help assess its performance
4. Return a decision to the user as to whether-or-not the company is a good investment on a numbers basis
   1. Provide a list of the metrics this was made on and what the threshold was to reach this recommendation
5. Return a decision to the user as to whether-or-not the company is a good investment on a sentiment basis from the report
   1. Provide a general sentiment analysis of whether the company is worried, stressed, or otherwise not confident in their own abilities
   2. NB: this may not return much as this language is often times dry and not full of worry, regardless if it is possible to see this then we will know.
