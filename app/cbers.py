"""app.cbers: handle request for CBERS."""

import os
import logging

import boto3

from remotepixel import cbers_ovr, cbers_full, cbers_ndvi

from aws_sat_api.search import cbers as cbers_search

logger = logging.getLogger('remotepixel_api')
logger.setLevel(logging.INFO)


def search(event, context):
    """Handle search requests."""
    path = event['path']
    row = event['row']
    data = list(cbers_search(path, row))
    info = {
        'request': {'path': path, 'row': row},
        'meta': {'found': len(data)},
        'results': data}
    return info


def overview(event, context):
    """Handle overview requests."""
    scene = event['scene']
    bands = event.get('bands', None)
    expression = event.get('expression')
    img_format = event.get('format', 'jpeg')
    if bands:
        bands = bands.split(',') if isinstance(bands, str) else bands
    return cbers_ovr.create(
        scene,
        bands=bands,
        expression=expression,
        img_format=img_format
    )


def ndvi(event, context):
    """Handle ndvi requests."""
    scene = event['scene']
    lat = float(event['lat'])
    lon = float(event['lon'])
    expression = event.get('expression')
    if not expression:
        expression = '(b8 - b7) / (b8 + b7)'
    res = cbers_ndvi.point(scene, [lon, lat], expression)
    res['ndvi'] = float('{0:.7f}'.format(res['ndvi']))
    return res


def ndvi_area(event, context):
    """Handle ndvi requests."""
    scene = event['scene']
    bbox = event['bbox']
    bbox = map(float, bbox.split(','))
    if len(bbox) != 4:
        raise Exception('BBOX must be a 4 values array')

    expression = event.get('expression')
    if not expression:
        expression = '(b5 - b4) / (b5 + b4)'

    return cbers_ndvi.area(scene, bbox, expression)


def full(event, context):
    """Handle full requests."""
    bucket = os.environ["OUTPUT_BUCKET"]
    scene = event['scene']
    bands = event.get('bands')
    expression = event.get('expression')
    if bands:
        bands = bands.split(',') if isinstance(bands, str) else bands

    mem = cbers_full.create(scene, bands=bands, expression=expression)

    params = {
        'ACL': 'public-read',
        'Metadata': {'scene': scene},
        'ContentType': 'image/tiff'}

    if expression:
        params['Metadata']['expression'] = expression
    else:
        params['Metadata']['bands'] = ''.join(map(str, bands))

    str_band = ''.join(map(str, bands))
    prefix = 'Exp' if expression else 'RGB'
    key = f'data/cbers/{scene}_{prefix}{str_band}.tif'

    client = boto3.client('s3')
    client.upload_fileobj(mem, bucket, key, ExtraArgs=params)

    return {
        'scene': scene,
        'path': f'https://s3.amazonaws.com/{bucket}/{key}'}
