"""app.landsat: handle request for Landsat-tiler"""

import os
import uuid
import logging

from remotepixel import l8_ovr, l8_full

from aws_sat_api.search import landsat as landsat_search

logger = logging.getLogger('remotepixel_api')
logger.setLevel(logging.INFO)


def search(event, context):
    """Handle search requests
    """
    path = event['path']
    row = event['row']
    full = event.get('full', True)
    data = list(landsat_search(path, row, full))
    info = {
        'request': {'path': path, 'row': row, 'full': full},
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
    return l8_ovr.create(scene, bands=bands, expression=expression, img_format=img_format)


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

    output_uid = str(uuid.uuid1())
    l8_full.create(scene, bucket, bands=bands, expression=expression, output_uid=output_uid)
    out_url = f'https://s3-us-west-2.amazonaws.com/{bucket}/data/landsat/{output_uid}.tif'
    return {'scene': scene, 'uuid': output_uid, 'path': out_url}
