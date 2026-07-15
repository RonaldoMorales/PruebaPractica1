PACKAGE := gamescout

.PHONY: install lint format run test

install:
	conda env create -f environment.yml

lint:
	flake8 --max-line-length=100 $(PACKAGE) tests

format:
	black $(PACKAGE) tests

run:
	python -m $(PACKAGE).main

test:
	pytest tests


