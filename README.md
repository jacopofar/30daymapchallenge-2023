## 30 day map challenge 2023

This is my playground for the [30 day map challenge](https://30daymapchallenge.com/).

In essence, for each day of November 2023 there's a theme and I try to produce a visualization on it.

I don't plan to follow the daily schedule too strictly, may skip days or do them later.

## How to run
You need `pdm` and `dotenv` installed, and a PostGIS instance initialized with some data (see the section about initializing the DB).

Install the dependencies with `pdm install`, then:

    dotenv run pdm run mapchallenge/day01.py


## Status

<table>
<th>
<td>day</td>
<td>theme</td>
<td>implementation</td>

</th>
<tr>
<td>1</td><td>Point</td><td>✔️ Benches and water fountains in Milan, italy, using single pixels</td>
</tr>
<tr>
<td>2</td><td>Line</td><td>✔️ Roads colored by the bike accessibility (dedicated, allowed, forbidden, unknown) in Milan.</td>

</tr>
</table>


## How to initialize a DB
You need Docker (or Podman).

Use `./ingest_pbf.sh filename.pbf` to start a PostGIS instance and ingest a PBF file in it using pgosm-flex from rustprooflabs. It will leave the DB running.

Later, use `make start-db` to restart the same instance with the data already loaded.

You can use QGIS to easily visualize the loaded data.