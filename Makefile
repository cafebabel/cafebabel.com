# Config
server=preprod@185.34.32.17
src_dir=~/cafebabel.com
venv_dir=~/cafebabel.com/venv
branch=master
LOGS=access

# Commands
remote=ssh -t ${server}
goto_src=cd ${src_dir} && source ${venv_dir}/bin/activate


help:
	@echo "Make tasks for installation and deployment. Refer to the Makefile content to know more."

logs:  # `make type=access` or `make type=errors` for displaying logs.
	@echo "> Reading ${type} logs."
	${remote} "${goto_src} && tail -f logs/${type}.log"

deploy:
	@echo "> Fetching master branch and updating sources."
	${remote} "${goto_src} && git fetch origin ${branch} && git checkout ${branch} && git reset --hard FETCH_HEAD"
	${remote} "${goto_src} && pip install -r requirements.txt"
	${remote} "pkill flask && source ~/cafebabel.com/venv/bin/activate && FLASK_APP=prod flask run >> ~/log/preprod-$(date +%Y%m%d).log 2>&1"

install:
	@echo "> Installing sources, dependencies and database."
	-${remote} "git clone https://github.com/cafebabel/cafebabel.com.git ${src_dir}"
	-${remote} "python3.6 -m venv ${venv_dir}"
	-${remote} "${goto_src} && mkdir logs"
	-${remote} "${goto_src} && mkdir -p cafebabel/static/uploads/{articles,users,tags}"
	make reset-db
	make deploy

reset-db:
	${remote} "${goto_src} && FLASK_APP=prod flask initdb"
	${remote} "${goto_src} && FLASK_APP=prod flask load_fixtures"
