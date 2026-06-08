.PHONY: init dev test brief dashboard deploy-check

init:
	python scripts/init_workspace.py

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	python -m unittest discover -s app/tests -p "*_test.py"

brief:
	python -m app.workflows.morning_brief

dashboard:
	python -m app.workflows.refresh_data

deploy-check:
	python -m app.workflows.deploy_check
