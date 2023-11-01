from PIL import Image, ImageDraw
from tqdm import tqdm

from mapchallenge.helpers.database import run_query
from mapchallenge.params import EXTENT, IMSIZE

if __name__ == "__main__":
    colors = dict(
        designated=(0, 255, 0, 255),
        allowed=(255, 255, 0, 255),
        no=(255, 0, 0, 255),
        unknown=(128, 128, 128, 127),
    )

    rows = run_query(
        """
            SELECT
            CASE
                WHEN ((tags ->> 'bicycle') = 'designated' OR (tags ->> 'highway') = 'cycleway') THEN 'designated'
                WHEN (tags ->> 'cycleway' = 'no' OR
                    (tags ->> 'bicycle' = 'yes' AND tags ->> 'highway' IN ('path', 'footway')) OR
                    (tags ->> 'cycleway:right') = 'lane' OR (tags ->> 'cycleway:left') = 'lane' OR
                    (tags ->> 'highway' = 'unclassified' AND tags ->> 'oneway:bicycle' = 'yes') OR
                    (tags ->> 'surface_bike' = 'milanese_paving') OR
                    (tags ->> 'foot' = 'yes' AND tags ->> 'bicycle' = 'yes'))
                    THEN 'allowed'
                WHEN ((tags ->> 'cycleway:right') = 'no' OR tags ->> 'cycleway:both' = 'no' OR
                    tags ->> 'bicycle' = 'dismount' OR tags ->> 'bicycle' = 'no') THEN 'no'
                ELSE 'unknown' END AS biking_status,
            st_transform(geom, 4326) as geom
        FROM
            osm.tags
                JOIN osm.road_line rl ON rl.osm_id = tags.osm_id
        WHERE
             tags ->> 'access' IS NULL OR tags ->> 'access' NOT IN ('private', 'no')
        AND geom && st_makeenvelope(%s, %s, %s, %s, 3857)
    """,
        EXTENT.as_epsg3857(),
    )
    im = Image.new("RGBA", IMSIZE, (0, 0, 0, 255))
    draw = ImageDraw.Draw(im)
    for row in tqdm(rows):
        road_polygon = EXTENT.geom_in_image_coords(row[1], im.size)
        assert (
            road_polygon.geom_type == "MultiLineString"
        ), f"Expected a MultiLineString got {road_polygon.type}"
        for line in road_polygon.geoms:
            # get consecutive coords
            coords = list(line.coords)
            for i in range(len(coords) - 1):
                draw.line(coords[i] + coords[i + 1], fill=colors[row[0]], width=1)
            # close the circle if it is
            if line.is_ring:
                draw.line(coords[-1] + coords[0], fill=colors[row[0]], width=1)
    im.save("day02.png", "PNG")
