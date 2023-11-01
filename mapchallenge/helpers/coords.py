from dataclasses import dataclass

from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform

TRAN_4326_TO_3857 = Transformer.from_crs("EPSG:4326", "EPSG:3857")


@dataclass
class ExtentDegrees:
    """Bounding box in WGS84 degrees. Aka EPSG:4326"""

    latmin: float
    latmax: float
    lonmin: float
    lonmax: float

    def enlarged(self, factor: float) -> "ExtentDegrees":
        """Calculate an extent enlarged in all directions.

        The factor is RELATIVE, 0 means no change, 1.0 means 100% larger,
        -0.5 means 50% smaller

        Parameters
        ----------
        factor : float
            How much to enlarge, e.g. 0.1 means 10% more
        """
        lat_mid = (self.latmax + self.latmin) / 2
        lat_radius = abs(self.latmax - self.latmin) / 2 * (1 + factor)
        lon_mid = (self.lonmax + self.lonmin) / 2
        lon_radius = abs(self.lonmax - self.lonmin) / 2 * (1 + factor)
        return ExtentDegrees(
            latmin=min(lat_mid - lat_radius, lat_mid + lat_radius),
            latmax=max(lat_mid - lat_radius, lat_mid + lat_radius),
            lonmin=min(lon_mid - lon_radius, lon_mid + lon_radius),
            lonmax=max(lon_mid - lon_radius, lon_mid + lon_radius),
        )

    def as_e7_dict(self) -> dict[str, int]:
        return dict(
            latmin=int(self.latmin * 10**7),
            latmax=int(self.latmax * 10**7),
            lonmin=int(self.lonmin * 10**7),
            lonmax=int(self.lonmax * 10**7),
        )

    def as_epsg3857(self) -> tuple[float, float, float, float]:
        """Convert the extent to a tuple in EPSG 3857.

        The order is the same required by PostGIS st_makeenvelope
        that is: lonmin, latmin, lonmax, latmax
        """
        lonmin, latmin = TRAN_4326_TO_3857.transform(self.latmin, self.lonmin)
        lonmax, latmax = TRAN_4326_TO_3857.transform(self.latmax, self.lonmax)
        return (lonmin, latmin, lonmax, latmax)

    def geom_in_image_coords(self, geom: shape, image_size: tuple[int, int]) -> shape:
        """Convert a geometry in EPSG 4326 to a pixel in an image.

        Parameters
        ----------
        geom : shape
            A Shapely geometry in EPSG 4326
        image_size : tuple
            A tuple of two integers, width and height
        """

        # TODO would be better to generate and cache the affine transformation
        # also, this function should handle sequences of coordinates
        # still, shapely detects this and iterates for us
        def transform_coords(
            x: float, y: float, z: float | None = None
        ) -> tuple[float, float]:
            x -= self.lonmin
            y -= self.latmin
            x /= self.lonmax - self.lonmin
            y /= self.latmax - self.latmin
            x *= image_size[0]
            # y is inverted, cartesian convention rather than image convention
            y = (1.0 - y) * image_size[1]
            return (x, y)

        return transform(transform_coords, geom)
