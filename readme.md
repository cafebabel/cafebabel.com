# Cafebabel


## Installation


### Requirements

- Python 3.6+
- MongoDB 3.4+


## Preparing the project

```
python3 -m venv ./venv
source ./venv/bin/activate
```

### Installing the dependencies

```
pip install -e .
```

### Installing the database

Install and launch MongoDB on default port (27017) or tune it in your
_settings.local.py_ (see [Configuring section](#Configuring)).

```
flask initdb
```

> You may reset your database by deleting the _/cafebabel.db_ file and
re-initializing the database.

### Configuring

If existing, the file `settings.local.py` at the root of the project will
override the default `settings.py` configuration.


## Running the project

```
export FLASK_APP=cafebabel
export FLASK_DEBUG=1
flask run
```


## Running a dummy mail server

```
sudo python -m smtpd -n -c DebuggingServer localhost:25
```


## Production installation

In order to deploy to the staging server, you should have an SSH access
to the server with the _cafebabel_ user callable via the command `ssh cafebabel`.

Your server must have python3.6 installed.

Installation can be processed with `make install`.
Deploying will run through `make deploy`.


## Documentation

### Architecture Decision Records

Please document important
[architecture decisions](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions),
you can use [adr-tools](https://github.com/npryce/adr-tools) for this.

Existing ones are located in `docs/architecture/decisions`.
