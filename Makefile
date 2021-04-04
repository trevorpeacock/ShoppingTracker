
venv:
	#sudo apt install make python3-virtualenv python3-tk sox
	virtualenv --python /usr/bin/python3 venv
	bash -c ". venv/bin/activate && pip install django openfoodfacts"

run_test: venv
	bash -c ". venv/bin/activate && python test.py"

run: venv
	bash -c ". venv/bin/activate && python run.py"

clean:
	rm -dfr venv
	rm -dfr build
	rm -dfr debian/.debhelper/generated/shoppingtracker/
	rm -dfr debian/shoppingtracker/
	rm debian/files
	rm debian/shoppingtracker.debhelper.log
	rm debian/shoppingtracker.postinst.debhelper
	rm debian/shoppingtracker.prerm.debhelper
	rm debian/shoppingtracker.substvars

build:
	dpkg-buildpackage -us -uc -b
	mkdir -p build
	mv ../shoppingtracker_* build/

install: build
	dpkg -i `ls build/*.deb | sort | tail -n 1`
