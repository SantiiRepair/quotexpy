.PHONY: clean get-deps

docs: clean
	sphinx-build -b html -d build/docs docs build/static/

server: clean
	python server.py 8080

install: get-deps
	pip install -e .

clean:
	rm -rf build/ dist/ MANIFEST .coverage .name htmlcov  2>/dev/null || true
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '._*' -exec rm -f {} +

get-deps:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pip install -r requirements-docs.txt