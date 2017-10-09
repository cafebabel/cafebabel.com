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
export FLASK_APP=app.py
export FLASK_DEBUG=1
flask initdb
```

> You may reset your database by deleting the _/cafebabel.db_ file and
re-initializing the database.


## Running the project

```
flask run
```


## Running a dummy mail server

```
sudo python -m smtpd -n -c DebuggingServer localhost:25
```


## Deploying

In order to deploy to the staging server, you should have an SSH access
to the server with the _cafebabel_ user callable via the command `ssh cafebabel`.

With that working, you may deploy using the command `make deploy`.
