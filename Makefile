
venv:
	#sudo apt install make python3-virtualenv python3-tk sox
	virtualenv --python /usr/bin/python3 venv
	bash -c ". venv/bin/activate && pip install django"

run_test: venv
	bash -c ". venv/bin/activate && python test.py"

run: venv
	bash -c ". venv/bin/activate && python app.py"

clean:
	rm -dfr venv
