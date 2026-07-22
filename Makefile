PACKAGE := gamescout

.PHONY: install lint format run dashboard test

install:
	conda env create -f environment.yml

lint:
	flake8 --max-line-length=100 gamescout app tests

format:
	black gamescout app tests

run:
	python -m $(PACKAGE).main

dashboard:
	python -m streamlit run app/dashboard.py

test:
	python -m pytest tests