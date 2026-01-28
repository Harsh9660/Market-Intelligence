.PHONY: install pipeline run api

install:
	pip install -r requirements.txt

pipeline:
	python pipeline.py

api:
	python manage.py runserver 8000

run:
	streamlit run streamlit_app/app.py

clean:
	rm -rf Data/data/*
	find . -type d -name "__pycache__" -exec rm -rf {} +
