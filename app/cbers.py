"""app.cbers: handle request for CBERS-tiler"""

import os
import logging

from remotepixel import cbers_ovr, cbers_full, cbers_ndvi

from aws_sat_api.search import cbers as cbers_search

logger = logging.getLogger('remotepixel_api')
logger.setLevel(logging.INFO)


def search(event, context):
    """Handle search requests
    """
    path = event['path']
    row = event['row']
    data = list(cbers_search(path, row))
    info = {
        'request': {'path': path, 'row': row},
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
    return cbers_ovr.create(scene, bands=bands, expression=expression, img_format=img_format)


def ndvi(event, context):
    """Handle ndvi requests
    """
    logger.info(event)

    scene = event['scene']
    lat = float(event['lat'])
    lon = float(event['lon'])
    expression = event.get('expression')
    if not expression:
        expression = '(b8 - b7) / (b8 + b7)'
    res = cbers_ndvi.point(scene, [lon, lat], expression)
    res['ndvi'] = float('{0:.7f}'.format(res['ndvi']))
    return res


def full(event, context):
    """Handle full requests
    """
    logger.info(event)

    bucket = os.environ["OUTPUT_BUCKET"]
    scene = event.get('scene')
    bands = event.get('bands')
    expression = event.get('expression')
    if event.get('bands'):
        bands = bands.split(',') if isinstance(bands, str) else bands

    out_key = cbers_full.create(scene, bucket, bands=bands, expression=expression)
    out_url = f'https://s3.amazonaws.com/{bucket}/{out_key}'
    return {'scene': scene, 'path': out_url}
