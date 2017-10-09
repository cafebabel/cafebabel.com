goto_src=cd ~/src && source ../venv/bin/activate

help:
	@echo "Make tasks for deployment. Checkout the makefile content."

deploy:
	@echo "Fetching master branch and updating sources."
	ssh cafebabel "${goto_src} && git fetch origin master && git checkout master && git reset --hard FETCH_HEAD"
	ssh cafebabel "${goto_src} && pip install -r requirements.txt"
	ssh cafebabel "${goto_src} && python app.py 0.0.0.0:5000 &"
