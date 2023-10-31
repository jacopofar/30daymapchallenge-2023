
## How to initialize a DB
Docker is required.
Use `./ingest_pbf.sh filename.pbf` to start a PostGIS instance and ingest a PBF file in it using pgosm-flex from rustprooflabs. It will leave the DB running.

Later, use `make start-db` to restart the same instance with the data already loaded.

You can use QGIS to easily visualize the loaded data.