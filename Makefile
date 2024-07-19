.PHONY: clean get-deps

install: get-deps
	pip install -e .

clean:
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '._*' -exec rm -f {} +

get-deps:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt