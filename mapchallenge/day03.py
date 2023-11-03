# type: ignore

from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm

from mapchallenge.helpers.database import run_query
from mapchallenge.helpers.drawing import add_vertical_legend, stamp_shape
from mapchallenge.params import EXTENT, IMSIZE

BACKGROUND_COLOR = (255, 230, 230, 255)

TRAFFIC_COLOR = (0, 0, 0)
NATURE_COLOR = (0, 255, 0)
USAGE_COLOR = (0, 0, 255)

OSM_TYPES_MAPPING = {
    "parking": TRAFFIC_COLOR,
    "parking_space": TRAFFIC_COLOR,
    "grass": NATURE_COLOR,
    "farmland": NATURE_COLOR,
    "residential": USAGE_COLOR,
    "pitch": USAGE_COLOR,
    "park": NATURE_COLOR,
    "garden": NATURE_COLOR,
    "industrial": USAGE_COLOR,
    "grassland": NATURE_COLOR,
    "forest": NATURE_COLOR,
    "scrub": NATURE_COLOR,
    "school": USAGE_COLOR,
    "playground": USAGE_COLOR,
    "place_of_worship": USAGE_COLOR,
    "retail": USAGE_COLOR,
    "swimming_pool": USAGE_COLOR,
    "wood": NATURE_COLOR,
    "allotments": NATURE_COLOR,
    "meadow": NATURE_COLOR,
    "farmyard": NATURE_COLOR,
    "commercial": USAGE_COLOR,
    "sports_centre": USAGE_COLOR,
    "construction": USAGE_COLOR,
    "dog_park": NATURE_COLOR,
    "kindergarten": USAGE_COLOR,
    "railway": TRAFFIC_COLOR,
    "brownfield": USAGE_COLOR,
    "flowerbed": NATURE_COLOR,
    "fuel": (255, 255, 255),
    "motorcycle_parking": TRAFFIC_COLOR,
    "greenhouse_horticulture": NATURE_COLOR,
    "restaurant": USAGE_COLOR,
    "cemetery": USAGE_COLOR,
    "recreation_ground": NATURE_COLOR,
    "religious": USAGE_COLOR,
    "sand": NATURE_COLOR,
    "community_centre": USAGE_COLOR,
    "shelter": USAGE_COLOR,
    "bench": NATURE_COLOR,
    "orchard": NATURE_COLOR,
    "fountain": NATURE_COLOR,
    "police": USAGE_COLOR,
    "bicycle_parking": TRAFFIC_COLOR,
    "track": NATURE_COLOR,
    "military": USAGE_COLOR,
    "social_facility": USAGE_COLOR,
    "village_green": NATURE_COLOR,
    "recycling": USAGE_COLOR,
    "car_wash": USAGE_COLOR,
    "cafe": USAGE_COLOR,
    "toilets": USAGE_COLOR,
    "hospital": USAGE_COLOR,
    "theatre": USAGE_COLOR,
    "tree_row": NATURE_COLOR,
    "quarry": NATURE_COLOR,
    "townhall": USAGE_COLOR,
    "trolley_bay": USAGE_COLOR,
    "university": USAGE_COLOR,
    "fast_food": USAGE_COLOR,
    "sports_hall": USAGE_COLOR,
    "marketplace": USAGE_COLOR,
    "plant_nursery": NATURE_COLOR,
    "public_building": USAGE_COLOR,
    "greenfield": NATURE_COLOR,
    "bar": USAGE_COLOR,
    "library": USAGE_COLOR,
    "bank": USAGE_COLOR,
    "garages": TRAFFIC_COLOR,
    "basin": NATURE_COLOR,
    "fitness_station": USAGE_COLOR,
    "post_office": USAGE_COLOR,
    "education": USAGE_COLOR,
    "heath": NATURE_COLOR,
    "stadium": USAGE_COLOR,
    "arts_centre": USAGE_COLOR,
    "cinema": USAGE_COLOR,
    "bleachers": USAGE_COLOR,
    "clinic": USAGE_COLOR,
    "reservoir": NATURE_COLOR,
    "shrubbery": NATURE_COLOR,
    "pub": USAGE_COLOR,
    "animal_keeping": NATURE_COLOR,
    "rescue_station": USAGE_COLOR,
    "taxi": TRAFFIC_COLOR,
    "fire_station": USAGE_COLOR,
    "animal_shelter": USAGE_COLOR,
    "golf_course": NATURE_COLOR,
    "studio": USAGE_COLOR,
    "childcare": USAGE_COLOR,
    "churchyard": USAGE_COLOR,
    "fitness_centre": USAGE_COLOR,
    "bus_station": TRAFFIC_COLOR,
    "horse_riding": NATURE_COLOR,
    "monastery": USAGE_COLOR,
    "nightclub": USAGE_COLOR,
    "doctors": USAGE_COLOR,
    "bicycle_rental": TRAFFIC_COLOR,
    "college": USAGE_COLOR,
    "nursing_home": USAGE_COLOR,
    "nature_reserve": NATURE_COLOR,
    "depot": USAGE_COLOR,
    "landfill": USAGE_COLOR,  # place where you want to go :)
    "grave_yard": USAGE_COLOR,  # idem
    "prison": USAGE_COLOR,  # oh, again
    "dance": USAGE_COLOR,
    "courthouse": USAGE_COLOR,
    "beach": NATURE_COLOR,
    "water_point": USAGE_COLOR,
    "social_centre": USAGE_COLOR,
    "outdoor_seating": USAGE_COLOR,
    "schoolyard": USAGE_COLOR,
    "water_park": NATURE_COLOR,
    "ice_cream": USAGE_COLOR,
    "bandstand": USAGE_COLOR,
    "pharmacy": USAGE_COLOR,
    "events_venue": USAGE_COLOR,
    "canteen": USAGE_COLOR,
    "fishing": NATURE_COLOR,
    "car_sharing": TRAFFIC_COLOR,
    "tree_group": NATURE_COLOR,
    "vineyard": NATURE_COLOR,
    "shower": USAGE_COLOR,
    "scree": NATURE_COLOR,
    "conference_centre": USAGE_COLOR,
    "waste_disposal": USAGE_COLOR,
    "conservation": NATURE_COLOR,
    "dressing_room": USAGE_COLOR,
    "game_feeding": NATURE_COLOR,
    "miniature_golf": NATURE_COLOR,
    "charging_station": TRAFFIC_COLOR,
    "reception_desk": USAGE_COLOR,
    "archive": USAGE_COLOR,
    "veterinary": USAGE_COLOR,
    "mortuary": USAGE_COLOR,
    "bird_hide": NATURE_COLOR,
    "traffic_island": TRAFFIC_COLOR,
    "post_depot": USAGE_COLOR,
    "food_court": USAGE_COLOR,
    "adult_gaming_centre": USAGE_COLOR,
    "retirement_home": USAGE_COLOR,
    "service": USAGE_COLOR,
    "apiary": NATURE_COLOR,
}


if __name__ == "__main__":
    rows = run_query(
        """
    WITH many_polygons AS (
        SELECT osm_type, geom FROM osm.landuse_polygon
            UNION ALL
        SELECT osm_type, geom FROM osm.leisure_polygon
            UNION ALL
        SELECT osm_type, geom FROM osm.natural_polygon
            UNION ALL
        SELECT osm_type, geom FROM osm.amenity_polygon
    )
    SELECT
        osm_type,
        st_transform(geom, 4326) AS geom
        FROM
        many_polygons
    WHERE
    geom && st_makeenvelope(%s, %s, %s, %s, 3857)
    """,
        EXTENT.as_epsg3857(),
    )
    im = Image.new("RGBA", IMSIZE, BACKGROUND_COLOR)
    for row in tqdm(rows):
        if row[0] not in OSM_TYPES_MAPPING:
            print(f"Unknown type {row[0]}")
            continue
        overlay = Image.new("RGBA", IMSIZE, (10, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        stamp_shape(
            EXTENT,
            draw,
            row[1],
            fill=OSM_TYPES_MAPPING[row[0]] + (100,),
        )
        im = Image.alpha_composite(im, overlay)
    # now add legend and title
    legend_extra_margin = 200
    title_top_margin = 100
    im_total = Image.new(
        "RGBA",
        (IMSIZE[0], IMSIZE[1] + legend_extra_margin + title_top_margin),
        BACKGROUND_COLOR,
    )
    im_total.paste(im, (0, title_top_margin))
    im_total_draw = ImageDraw.Draw(im_total)

    add_vertical_legend(
        im_total_draw,
        [
            ("Nature", NATURE_COLOR),
            ("Traffic", TRAFFIC_COLOR),
            ("Usage", USAGE_COLOR),
        ],
        (10, IMSIZE[1] + title_top_margin + 5),
        legend_extra_margin - 10,
    )
    im_total_draw.text(
        (20, 20),
        "Milan, Italy - landuse map",
        fill="black",
        font=ImageFont.load_default().font_variant(size=60),
    )
    im_total.save("day03.png")
