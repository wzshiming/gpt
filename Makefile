
EXE = dist/gpt

all: $(EXE) test

dist/%: %.spec %.py venv/bin/pyinstaller
	venv/bin/pyinstaller -y $<

.PHONY: test
test: venv
	venv/bin/python gpt.py version

venv:
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt

venv/bin/pyinstaller: venv
	venv/bin/pip install pyinstaller
