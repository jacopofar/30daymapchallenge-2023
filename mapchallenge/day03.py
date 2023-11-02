from PIL import Image, ImageDraw
from tqdm import tqdm

from mapchallenge.helpers.database import run_query
from mapchallenge.helpers.drawing import stamp_shape
from mapchallenge.params import EXTENT, IMSIZE

if __name__ == "__main__":
    rows = run_query(
        """
        WITH
    many_polygons AS (SELECT
                          name,
                          osm_type,
                          geom
                      FROM
                          osm.landuse_polygon
                      UNION ALL
                      SELECT
                          name,
                          osm_type,
                          geom
                      FROM
                          osm.leisure_polygon
                      UNION ALL
                      SELECT
                          name,
                          osm_type,
                          geom
                      FROM
                          osm.natural_polygon
                      UNION ALL
                      SELECT
                          name,
                          osm_type,
                          geom
                      FROM
                          osm.amenity_polygon
                      )
        SELECT
            st_transform(geom, 4326) as geom
        FROM
            many_polygons
        WHERE
        geom && st_makeenvelope(%s, %s, %s, %s, 3857)
    """,
        EXTENT.as_epsg3857(),
    )
    im = Image.new("RGBA", IMSIZE, (10, 0, 0, 255))
    draw = ImageDraw.Draw(im)
    for row in tqdm(rows):
        # TODO add alpha blending, it's not automatic!
        stamp_shape(
            EXTENT, draw, row[0], fill=(0, 0, 0, 10), outline=(255, 0, 0, 255), width=1
        )
    im.save("day03.png", "PNG")
