# Cafebabel


## Installation


### Requirements

- Python 3.6+
- MongoDB 3.4+


## Preparing the project

```
python3 -m venv ./venv
source ./venv/bin/activate
mkdir -p static/uploads/{archives,articles,tags,users,resized-images}
export FLASK_APP=dev.py
export FLASK_DEBUG=1
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


## Running the project

```
flask run
```

As previously for `flask initdb`, make sure you have exported the `FLASK_APP`
environment variable.


## Running a dummy mail server

```
sudo python -m smtpd -n -c DebuggingServer localhost:25
```


## Production installation

In order to deploy to the staging server, you should have an SSH access
to the server.

Your server must have python3.6 installed, MongoDB running and the
_settings.py_ (or _settings.local.py_) file properly setup.

> In the commands below, `preprod` should be replaced by "`prod`" for
publishing to the _prod_ instance.

- Installation can be processed with `make install env=preprod`.
- Deploying will run through `make deploy env=preprod`.
- Error logs can be accessed by `make logs env=preprod type=access`.
Replace `access` by `error` for the error logs.

> View the _Makefile_ for further comprehension or more commands.

## Documentation

### Architecture Decision Records

Please document important
[architecture decisions](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions),
you can use [adr-tools](https://github.com/npryce/adr-tools) for this.

Existing ones are located in `docs/architecture/decisions`.
