from PIL import ImageDraw, ImageFont
from shapely.geometry import shape

from mapchallenge.helpers.coords import ExtentDegrees


def stamp_shape(ext: ExtentDegrees, imd: ImageDraw, shape: shape, **kwargs) -> None:
    """Draw a Shapely shape on an image.

    Coordinates are converted assuming the given extent represents the
    area covered by the image.

    Extra arguments are given to Pillow ImageDraw methods for color, width,
    etc.

    Unfortunately polygon with holes are not supported (they will be "filled").
    """
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
        # TODO polygon with holes are not supported
        # Shapely triangulation also doesn't support holes
        # see https://github.com/shapely/shapely/issues/518
        # some specific algorithm is needed, but I could not find
        # nothing available and practically usable here
        # could be an interesting side project

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


def add_vertical_legend(
    imd: ImageDraw,
    text_colors: dict[str, any],
    start_point: tuple[int, int],
    max_height: int,
) -> None:
    """Paint a vertical legend using the given space.

    Each element of the legend has a color, the size of the squares and the
    font size will be chosen to fit.
    """
    ftf = ImageFont.load_default()
    legend_position = start_point[1]
    element_height = max_height // len(text_colors)
    padding = element_height // 4
    square_size = padding * 2
    # find font size that fits
    for fs in range(1, 100, 2):
        bbox = ftf.font_variant(size=fs).getbbox("X")
        if bbox[3] - bbox[1] > square_size:
            break
    ftf = ftf.font_variant(size=fs - 2)
    for text, color in text_colors:
        imd.rectangle(
            (
                (start_point[0], legend_position),
                (start_point[0] + square_size, legend_position + square_size),
            ),
            fill=color,
        )
        imd.text(
            (start_point[0] + square_size + padding, legend_position),
            text,
            fill="black",
            font=ftf,
        )
        legend_position += element_height
