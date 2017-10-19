# Defaults
branch=mailjet-smtp
LOGS=access

# Commands
goto_src=cd ~/src && source ~/venv/bin/activate


help:
	@echo "Make tasks for deployment. Read the Makefile content."

logs:  # LOG=<access|errors>
	@echo "> Reading ${LOGS} logs."
	ssh cafebabel "${goto_src} && tail -f logs/${LOGS}.log"

deploy:
	@echo "> Fetching master branch and updating sources."
	ssh cafebabel "${goto_src} && git fetch origin ${branch} && git checkout ${branch} && git reset --hard FETCH_HEAD"
	ssh cafebabel "${goto_src} && pip install -r requirements.txt"
	-ssh cafebabel "${goto_src} && pkill gunicorn"
	ssh cafebabel "${goto_src} && SETTINGS_PATH=`pwd`/settings.prod.py gunicorn -w 4 -b 0.0.0.0:5000 app:app --access-logfile logs/access.log --error-logfile logs/errors.log > /dev/null"
	@echo "< Deployed!"

install:
	@echo "> Installing sources, dependencies and database."
	ssh cafebabel "git clone https://github.com/cafebabel/cafebabel.com.git ~/src"
	ssh cafebabel "python3.6 -m venv ~/venv"
	ssh cafebabel "${goto_src} && mkdir logs"
	ssh cafebabel "${goto_src} && pip install -r requirements.txt"

reset-db:
	ssh cafebabel "${goto_src} && FLASK_APP=app.py flask initdb"
