.PHONY: start-db
start-db:
	./start_db.sh

.PHONY: format
format:
	pdm run isort mapchallenge
	pdm run ruff format mapchallenge

.PHONY: mypy
mypy:
	pdm run mypy --strict --explicit-package-bases mapchallenge