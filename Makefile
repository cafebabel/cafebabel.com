goto_src=cd ~/src && source ~/venv/bin/activate

help:
	@echo "Make tasks for deployment. Checkout the makefile content."

deploy:
	@echo "> Fetching master branch and updating sources."
	ssh cafebabel "${goto_src} && git fetch origin master && git checkout master && git reset --hard FETCH_HEAD"
	ssh cafebabel "${goto_src} && pip install -r requirements.txt"
	ssh cafebabel "${goto_src} && python app.py 0.0.0.0:5000 &"

install:
	@echo "> Installing sources, dependencies and database."
	ssh cafebabel "git clone https://github.com/cafebabel/cafebabel.com.git ~/src"
	ssh cafebabel "python3.6 -m venv ~/venv"
	ssh cafebabel "${goto_src} && pip install -r requirements.txt"
	ssh cafebabel "${goto_src} && FLASK_APP=app.py flask initdb"
