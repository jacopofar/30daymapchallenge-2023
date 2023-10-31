.PHONY: start-db
start-db:
	./start_db.sh

.PHONY: format
format:
	pdm run ruff format mapchallenge

.PHONY: mypy
mypy:
	pdm run mypy --explicit-package-bases mapchallenge