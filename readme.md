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

### Setting the application

Set the `FLASK_APP` environment variable, it can be `dev.py` or `prod.py`
for instance. You can create another file for a particular env though.

```
export FLASK_APP=dev.py
```



### Installing the database

Install and launch MongoDB on default port (27017) or tune it in your
_instance/config.local.py_ (see [Configuring section](#Configuring)).

```
flask initdb
```


### Configuring

If existing, the file `instance/config.local.py` at the root of
the project will override the default `config.py` configuration.

Do not forget to create the folder dedicated to statics, by default:

```
mkdir -p static/uploads/articles
```


## Running the project

```
flask run
```


## Running a dummy mail server

```
sudo python -m smtpd -n -c DebuggingServer localhost:25
```


## Production installation

In order to deploy to the staging server, you should have an SSH access
to the server.

Your server must have python3.6 installed.

Installation can be processed with `make install`.
Deploying will run through `make deploy`.


## Documentation

### Architecture Decision Records

Please document important
[architecture decisions](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions),
you can use [adr-tools](https://github.com/npryce/adr-tools) for this.

Existing ones are located in `docs/architecture/decisions`.
