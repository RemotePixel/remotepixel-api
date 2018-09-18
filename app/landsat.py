"""app.landsat: handle request for Landsat."""

import os
import json
import uuid
import logging

import boto3

from remotepixel import l8_ovr, l8_full, l8_ndvi

from aws_sat_api.search import landsat as landsat_search

logger = logging.getLogger('remotepixel_api')
logger.setLevel(logging.INFO)


def search(event, context):
    """Handle search requests."""
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
    """Handle overview requests."""
    scene = event['scene']
    bands = event.get('bands')
    expression = event.get('expression')
    img_format = event.get('format', 'jpeg')
    if bands:
        bands = bands.split(',') if isinstance(bands, str) else bands
    return l8_ovr.create(
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
        expression = '(b5 - b4) / (b5 + b4)'
    res = l8_ndvi.point(scene, [lon, lat], expression)
    res['ndvi'] = float('{0:.7f}'.format(res['ndvi']))
    return res


def ndvi_area(event, context):
    """Handle ndvi requests."""
    scene = event['scene']
    bbox = event['bbox']
    bbox = list(map(float, bbox.split(',')))
    if len(bbox) != 4:
        raise Exception('BBOX must be a 4 values array')

    expression = event.get('expression')
    if not expression:
        expression = '(b5 - b4) / (b5 + b4)'

    return l8_ndvi.area(scene, bbox, expression)


def mosaic(event, context):
    """Handle mosaic requests."""
    bucket = os.environ["OUTPUT_BUCKET"]
    scenes = event.get('scenes')
    bands = event.get('bands')
    # expression = event.get('expression')
    if bands:
        bands = bands.split(',') if isinstance(bands, str) else bands

    mem, bounds = l8_full.mosaic(scenes, bands=bands)

    uid = str(uuid.uuid1())
    params = {
        'ACL': 'public-read',
        'Metadata': {'uuid': uid},
        'ContentType': 'image/tiff'}
    key = f'data/mosaic/{uid}_mosaic.tif'

    client = boto3.client('s3')
    client.upload_fileobj(mem, bucket, key, ExtraArgs=params)

    meta = {
        'id': uid,
        'mosaic': f'{uid}_mosaic.tif',
        'coordinates': {
            'north': bounds[3],
            'west': bounds[0],
            'south': bounds[1],
            'east': bounds[2],
            'Proj': 'EPSG:4326'}}

    params = {
        'ACL': 'public-read',
        'Metadata': {'uuid': uid},
        'ContentType': 'application/json'}
    key = f'data/mosaic/{uid}.json'

    client.upload_fileobj(json.dumps(meta), bucket, key, ExtraArgs=params)


def full(event, context):
    """Handle full requests."""
    bucket = os.environ["OUTPUT_BUCKET"]
    scene = event['scene']
    bands = event.get('bands')
    expression = event.get('expression')
    if bands:
        bands = bands.split(',') if isinstance(bands, str) else bands

    mem = l8_full.create(scene, bands=bands, expression=expression)

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
    key = f'data/landsat/{scene}_{prefix}{str_band}.tif'

    client = boto3.client('s3')
    client.upload_fileobj(mem, bucket, key, ExtraArgs=params)

    return {
        'scene': scene,
        'path': f'https://s3-us-west-2.amazonaws.com/{bucket}/{key}'}
