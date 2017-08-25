include Makefile.local.mk


$(VENV)/bin/python: requirements.txt requirements-dev.txt
	$(VENV)/bin/pip install -r requirements.txt -r requirements-dev.txt
	touch --no-create $(VENV)/bin/python

requirements-dev.txt: requirements-dev.in
	$(VENV)/bin/pip-compile requirements-dev.in -o requirements-dev.txt
