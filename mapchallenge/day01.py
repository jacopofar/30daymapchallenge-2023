from PIL import Image, ImageDraw

from mapchallenge.helpers.database import run_query
from mapchallenge.helpers.drawing import stamp_shape
from mapchallenge.params import EXTENT, IMSIZE

if __name__ == "__main__":
    ext = EXTENT
    relevant_types = dict(
        bench=(0, 255, 0, 128),
        drinking_water=(0, 0, 255, 128),
        parking=(128, 128, 128, 128),
    )

    rows = run_query(
        """
                SELECT
                    osm_type, st_transform(geom, 4326)
                FROM
                    osm.amenity_point
                WHERE
                    osm_type = ANY(%s)
                AND
                     geom && st_makeenvelope(
                        %s, %s,
                        %s, %s,
                        3857
                    );
    """,
        (list(relevant_types.keys()),) + ext.as_epsg3857(),
    )
    im = Image.new("RGBA", IMSIZE, (0, 0, 0, 255))
    draw = ImageDraw.Draw(im)
    for row in rows:
        stamp_shape(EXTENT, draw, row[1], fill=relevant_types[row[0]])
    im.save("day01.png", "PNG")
