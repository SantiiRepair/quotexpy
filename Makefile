.PHONY: clean get-deps

html: clean
	sphinx-build -b html -d build/docs/doctrees docs build/docs/html/

server: clean
	python server.py 8080

install: get-deps
	pip install -e .

tx-pull:
	cd docs/_locale/ \
	&& tx pull -af

tx-push:
	cd docs/_locale/ \
	&& sphinx-build -b gettext -E .. _pot \
	&& sphinx-intl update-txconfig-resources -p _pot -d . --transifex-project-name bottle \
	&& tx push -s

tx:
	$(MAKE) tx-push
	$(MAKE) tx-pull

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