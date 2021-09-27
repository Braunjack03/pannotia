import math
import logging
import requests
import os
from io import BytesIO
from PIL import Image, ImageDraw

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s.%(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger()


def deg_to_num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = (lon_deg + 180.0) / 360.0 * n
    ytile = (1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n
    return xtile, ytile


def num_to_deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg


def make_bounds_square(bounds, zoom):
    x1, y1 = deg_to_num(bounds[0], bounds[1], zoom)
    x2, y2 = deg_to_num(bounds[2], bounds[3], zoom)
    xc = (x1 + x2) / 2
    yc = (y1 + y2) / 2
    l = max((abs(x1 - x2), abs(y1 - y2)))
    lat1, lon1 = num_to_deg(xc - l / 2, yc - l / 2, zoom)
    lat2, lon2 = num_to_deg(xc + l / 2, yc + l / 2, zoom)
    llmin = (min([lat1, lat2]), min([lon1, lon2]))
    llmax = (max([lat1, lat2]), max([lon1, lon2]))
    bounds = [llmin[0], llmin[1], llmax[0], llmax[1]]
    return bounds


def get_image_cluster(lat_deg, lon_deg, lat_max, lon_max, dlat, dlon, zoom, url, max_res=2000, buf=0, res=512):
    zoom = int(zoom)
    xmin, ymax = deg_to_num(lat_deg - dlat, lon_deg - dlon, zoom)
    xmax, ymin = deg_to_num(lat_max + dlat, lon_max + dlon, zoom)

    while (xmax - xmin + 1) * res - 1 > max_res or (ymax - ymin + 1) * res - 1 > max_res:
        logger.warning(f'image size too big resizing:{((xmax - xmin + 1) * res - 1, (ymax - ymin + 1) * res - 1)}')
        zoom = int(zoom - 1)
        xmin, ymax = deg_to_num(lat_deg - dlat, lon_deg - dlon, zoom)
        xmax, ymin = deg_to_num(lat_max + dlat, lon_max + dlon, zoom)

    xmin, ymax = list(map(int, deg_to_num(lat_deg - dlat, lon_deg - dlon, zoom)))
    xmax, ymin = list(map(int, deg_to_num(lat_max + dlat, lon_max + dlon, zoom)))

    cluster = Image.new('RGB', ((xmax - xmin + 1) * res - 1, (ymax - ymin + 1) * res - 1))
    for xtile in range(xmin, xmax + 1):
        for ytile in range(ymin, ymax + 1):
            imgurl = None
            response = None
            try:
                imgurl = url.format(zoom, xtile, ytile)
                logger.debug("Opening: " + imgurl)
                response = requests.get(imgurl)
                tile = Image.open(BytesIO(response.content))
                cluster.paste(tile, box=((xtile - xmin) * res, (ytile - ymin) * res))
            except Exception as e:
                print(f'url:{imgurl}')
                print(f'response:{response}')
                print(e)
                logger.warning("Couldn't download image")

    (nx, ny) = cluster.size
    lat1, lon1 = num_to_deg(xmin, ymin, zoom)
    lat2, lon2 = num_to_deg(xmax + 1, ymax + 1, zoom)
    llmin = (min([lat1, lat2]), min([lon1, lon2]))
    llmax = (max([lat1, lat2]), max([lon1, lon2]))
    dx = (llmax[1] - llmin[1]) / nx
    dy = (llmin[0] - llmax[0]) / ny
    logger.debug(f'{llmin} {llmax} {dx} {dy}')
    uly = int((lat_max - llmax[0]) / dy)
    ulx = int((lon_deg - llmin[1]) / dx)
    lry = int((lat_deg - llmax[0]) / dy)
    lrx = int((lon_max - llmin[1]) / dx)
    if buf > 0:
        logger.debug(f'Drawing rectangle {((ulx, uly), (lrx, lry))}')
        draw = ImageDraw.Draw(cluster)
        for i in range(4):
            draw.rectangle(((ulx - i, uly - i), (lrx + i, lry + i)), outline=(0, 0, 255))
    cluster = cluster.crop((ulx - buf, uly - buf, lrx + buf, lry + buf))
    return cluster


def add_image_as_bytes(data, url, max_res=2000, buf=0):
    lat_min = min(data['bounds'][0::2])
    lat_max = max(data['bounds'][0::2])
    lon_min = min(data['bounds'][1::2])
    lon_max = max(data['bounds'][1::2])
    dlat = (lat_max - lat_min) / 4
    dlon = (lon_max - lon_min) / 4
    logger.info(f'Extracting data for {data["bounds"]}')
    img = get_image_cluster(lat_min, lon_min, lat_max, lon_max, dlat, dlon, data['zoom'], url, max_res=max_res, buf=buf)
    img_io = BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    data['image'] = img_io
    data['ratio'] = img.size[0] / img.size[1]


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import numpy as np

    mapbox_creds = {
        "mapbox_key": os.environ.get("mapbox_key"),
        "mapbox_id": os.environ.get("mapbox_id"),
    }
    map_url = r"https://api.mapbox.com/styles/v1/pangeamaps/{mapbox_id}/tiles/{0}/{1}/{2}?access_token={mapbox_key}".format(
        '{0}', '{1}', '{2}', **mapbox_creds)

    data = {
        'bounds': [-27.5, 153.0, -27.0, 153.5],
        'zoom': 11,
    }
    add_image_as_bytes(data, map_url, buf=50)

    im = Image.open(data['image'])

    fig = plt.figure()
    fig.patch.set_facecolor('white')
    plt.imshow(np.asarray(im))
    plt.show()
