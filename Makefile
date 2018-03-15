# Config
server=${env}@185.34.32.17
src_dir=~/cafebabel.com
venv_dir=~/cafebabel.com/venv
branch=master
old_prod=prod@91.194.60.65
old_prod_media_dir=~/cafebabel/data/medias
prod_server=127.0.0.1:5001
preprod_server=127.0.0.1:5000

# Commands
remote=ssh -t ${server}
goto_src=cd ${src_dir} && source ${venv_dir}/bin/activate


help:
	@echo "Make tasks for installation and deployment. Refer to the Makefile content to know more."

logs:  # type=error|access
	@${remote} "tail -f ~/log/${type}.log"

flush-logs:  # type=error|access
	@${remote} "echo '' > ~/log/${type}.log"
	@echo "Log file emptied!"

deploy:  # env=prod|preprod
	@echo "\n> Fetching master branch and updating sources."
	${remote} "${goto_src} && git fetch origin ${branch} && git checkout ${branch} && git reset --hard FETCH_HEAD"
	${remote} "${goto_src} && pip install -r requirements.txt"
	make sync_archives_media
	@echo "\n> Launching gunicorn daemon."
	${remote} "${goto_src} && pkill gunicorn 2> /dev/null; \
		gunicorn --daemon -b ${${env}_server} ${env}:app \
		--error-logfile ~/log/error-`date +%Y%m%d`.log --access-logfile ~/log/access-`date +%Y%m%d`.log"
	@echo "\n> App is deployed. Run \`make logs env=${env} type=access|error\` to follow activity."

sync_archives_media:
	@echo "\n> Synchronizing archives media from old production server."
	${remote} "rsync --archive --compress --human-readable --inplace --progress ${old_prod}:${old_prod_media_dir}/avatars/ ${src_dir}/cafebabel/uploads/users/"
	${remote} "rsync --archive --compress --human-readable --inplace --progress ${old_prod}:${old_prod_media_dir}/editorials/ ${src_dir}/cafebabel/uploads/articles/"
	${remote} "rsync --archive --compress --human-readable --inplace --progress ${old_prod}:${old_prod_media_dir}/cache/ ${src_dir}/cafebabel/uploads/archives/"

install:  # env=prod|preprod
	@echo "\n> Installing sources, dependencies and database."
	-${remote} "git clone https://github.com/cafebabel/cafebabel.com.git ${src_dir}"
	-${remote} "python3.6 -m venv ${venv_dir}"
	-${remote} "${goto_src} && make make_dirs"
	make deploy

make_dirs:
	mkdir -p ./logs
	mkdir -p ./cafebabel/uploads/{archives,articles,tags,users}
