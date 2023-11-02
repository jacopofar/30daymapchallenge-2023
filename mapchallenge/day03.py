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
            st_transform(geom, 4326) as geom
        FROM
            osm.building_polygon
        WHERE
        geom && st_makeenvelope(%s, %s, %s, %s, 3857)
    """,
        EXTENT.as_epsg3857(),
    )
    im = Image.new("RGBA", IMSIZE, (0, 0, 0, 255))
    draw = ImageDraw.Draw(im)
    for row in tqdm(rows):
        building_polygon = EXTENT.geom_in_image_coords(row[0], im.size)
        assert (
            building_polygon.geom_type == "MultiPolygon"
        ), f"Expected a MultiPolygon got {building_polygon.type}"
        for polygon in building_polygon.geoms:
            if polygon.boundary.geom_type == "LineString":
                coords = list(polygon.boundary.coords)
                draw.line(coords, fill="red", width=1)
            elif polygon.boundary.geom_type == "MultiLineString":
                for line in polygon.boundary.geoms:
                    coords = list(line.coords)
                    draw.line(coords, fill="red", width=1)
    im.save("day03.png", "PNG")
