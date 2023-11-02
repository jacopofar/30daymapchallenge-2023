from PIL import ImageDraw
from shapely.geometry import shape

from mapchallenge.helpers.coords import ExtentDegrees


def stamp_shape(ext: ExtentDegrees, imd: ImageDraw, shape: shape, **kwargs) -> None:
    shape = ext.geom_in_image_coords(shape, imd.im.size)
    if shape.geom_type == "Point":
        imd.point((shape.x, shape.y), **kwargs)
    elif shape.geom_type == "MultiLineString":
        for line in shape.geoms:
            # get consecutive coords
            coords = list(line.coords)
            for i in range(len(coords) - 1):
                imd.line(coords[i] + coords[i + 1], **kwargs)
            # close the circle if it is
            if line.is_ring:
                imd.line(coords[-1] + coords[0], **kwargs)
    elif shape.geom_type == "MultiPolygon":
        for polygon in shape.geoms:
            if polygon.boundary.geom_type == "LineString":
                coords = list(polygon.boundary.coords)
                imd.polygon(coords, **kwargs)
            elif polygon.boundary.geom_type == "MultiLineString":
                for line in polygon.boundary.geoms:
                    coords = list(line.coords)
                    imd.polygon(coords, **kwargs)
    else:
        raise NotImplementedError(f"Unknown shape {shape.geom_type}")
