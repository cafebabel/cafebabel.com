# Defaults
branch=master
LOGS=access

# Commands
server=cafebabel@51.15.138.163
goto_src=cd ~/src && source ~/venv/bin/activate


help:
	@echo "Make tasks for deployment. Read the Makefile content."

logs:  # LOG=<access|errors>
	@echo "> Reading ${LOGS} logs."
	ssh ${server} "${goto_src} && tail -f logs/${LOGS}.log"

deploy:
	@echo "> Fetching master branch and updating sources."
	ssh ${server} "${goto_src} && git fetch origin ${branch} && git checkout ${branch} && git reset --hard FETCH_HEAD"
	ssh ${server} "${goto_src} && pip install -r requirements.txt"
	-ssh ${server} "${goto_src} && pkill gunicorn"
	ssh ${server} "${goto_src} && gunicorn -w 4 -b 0.0.0.0:5000 app:app --access-logfile logs/access.log --error-logfile logs/errors.log &"

install:
	@echo "> Installing sources, dependencies and database."
	ssh ${server} "git clone https://github.com/cafebabel/cafebabel.com.git ~/src"
	ssh ${server} "python3.6 -m venv ~/venv"
	ssh ${server} "${goto_src} && mkdir logs"
	ssh ${server} "${goto_src} && mkdir -p static/uploads/articles"
	ssh ${server} "${goto_src} && pip install -r requirements.txt"

reset-db:
	ssh ${server} "${goto_src} && FLASK_APP=app.py flask initdb"
