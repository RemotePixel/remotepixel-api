"""sentinel handler function"""

# import os
# import json
import logging

from aws_sat_api.search import sentinel2 as sentinel_search

from remotepixel import s2_ovr  # ,s2_full

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


# def full(event, context):
#     """Handle full requests
#     """
#     logger.info(event)
#
#     bucket = os.environ.get("OUTPUT_BUCKET")
#
#     scene = info.get('scene')
#     if event.get('bands'):
#         bands = event.get('bands')
#         bands = bands.split(',') if isinstance(bands, str) else bands
#     expression = event.get('expression')
#
#     s2_full.create(scene, bucket, bands)
#     str_band = ''.join(map(str, bands))
#     outfname = f'{scene}_B{str_band}.tif'
#
#     out_url = f'https://s3-eu-central-1.amazonaws.com/{bucket}/data/landsat/{outfname}'
#     return json.dumps({'path': out_url})
