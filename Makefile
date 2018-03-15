# Config
server=preprod@185.34.32.17
src_dir=~/cafebabel.com
venv_dir=~/cafebabel.com/venv
branch=master
LOGS=access
old_prod=prod@91.194.60.65
old_prod_media_dir=~/cafebabel/data/medias

# Commands
remote=ssh -t ${server}
goto_src=cd ${src_dir} && source ${venv_dir}/bin/activate


help:
	@echo "Make tasks for installation and deployment. Refer to the Makefile content to know more."

logs:
	@${remote} "tail -f ~/log/preprod.log"

flush-logs:
	@${remote} "echo '' > ~/log/preprod.log"
	@echo "Log file emptied!"

deploy:
	@echo "> Fetching master branch and updating sources."
	${remote} "${goto_src} && git fetch origin ${branch} && git checkout ${branch} && git reset --hard FETCH_HEAD"
	${remote} "${goto_src} && pip install -r requirements.txt"
	make rsync
	@echo "> Launching gunicorn daemon."
	${remote} "${goto_src} && pkill gunicorn; \
		gunicorn --daemon -b 127.0.0.1:5000 preprod:app \
		--error-logfile ~/log/preprod.log --access-logfile ~/log/preprod.log"
	@echo "> App is deployed. Run \`make logs\` to follow activity."

rsync:
	@echo "> Synchronizing archives media from old production server."
	${remote} "rsync --archive --compress --human-readable --inplace --progress ${old_prod}:${old_prod_media_dir}/avatars/ ${src_dir}/cafebabel/uploads/users/"
	${remote} "rsync --archive --compress --human-readable --inplace --progress ${old_prod}:${old_prod_media_dir}/editorials/ ${src_dir}/cafebabel/uploads/articles/"
	${remote} "rsync --archive --compress --human-readable --inplace --progress ${old_prod}:${old_prod_media_dir}/cache/ ${src_dir}/cafebabel/uploads/archives/"

install:
	@echo "> Installing sources, dependencies and database."
	-${remote} "git clone https://github.com/cafebabel/cafebabel.com.git ${src_dir}"
	-${remote} "python3.6 -m venv ${venv_dir}"
	-${remote} "${goto_src} && make make-dirs"
	make reset-db
	make deploy

make-dirs:
	mkdir -p ./logs

reset-db:
	make flask-command command=initdb
	make flask-command command=load_fixtures

flask-command:
	${remote} "${goto_src} && FLASK_APP=prod flask ${command}"
