"""app.sentinel: handle request for sentinel"""

import logging

from aws_sat_api.search import sentinel2 as sentinel_search

from remotepixel import s2_ovr, s2_ndvi

logger = logging.getLogger('remotepixel_api')
logger.setLevel(logging.INFO)


def search(event, context):
    """Handle search requests
    """
    utm = event['utm']
    lat = event['lat']
    grid = event['grid']
    level = event.get('level', 'l1c')
    full = event.get('full', True)
    data = list(sentinel_search(utm, lat, grid, full, level))
    info = {
        'request': {'utm': utm, 'lat': lat, 'grid': grid, 'full': full, 'level': level},
        'meta': {'found': len(data)},
        'results': data}

    return info


def overview(event, context):
    """Handle overview requests
    """
    logger.info(event)

    scene = event['scene']
    bands = event.get('bands', None)
    expression = event.get('expression')
    img_format = event.get('format', 'jpeg')
    if bands:
        bands = bands.split(',') if isinstance(bands, str) else bands
    return s2_ovr.create(scene, bands=bands, expression=expression, img_format=img_format)


def ndvi(event, context):
    """Handle ndvi requests
    """
    logger.info(event)

    scene = event['scene']
    lat = float(event['lat'])
    lon = float(event['lon'])
    expression = event.get('expression')
    if not expression:
        expression = '(b08 - b04) / (b08 + b04)'
    res = s2_ndvi.point(scene, [lon, lat], expression)
    res['ndvi'] = float('{0:.7f}'.format(res['ndvi']))
    return res


def ndvi_area(event, context):
    """Handle ndvi requests
    """
    scene = event['scene']
    bbox = event['bbox']
    bbox = list(map(float, bbox.split(',')))
    if len(bbox) != 4:
        raise Exception('BBOX must be a 4 values array')

    expression = event.get('expression')
    if not expression:
        expression = '(b08 - b04) / (b08 + b04)'

    return s2_ndvi.area(scene, bbox, expression)
