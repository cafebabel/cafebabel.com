# Cafebabel


## Installation


### Requirements

Python 3.6+


## Preparing the project

```
python3 -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.txt
```

### Install the database

```
export FLASK_APP=cli.py
flask initdb
```

> You may reset your database by deleting the _/cafebabel.db_ file and
re-initializing the database.


## Running the project

```
python app.py
```
