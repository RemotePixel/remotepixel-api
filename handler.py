"""handler function"""

import os
import json
import uuid
import logging

from remotepixel import (l8_ovr,
                         l8_full,
                         l8_mosaic,
                         l8_ndvi,
                         srtm_mosaic,
                         s2_ovr,
                         s2_full)

logger = logging.getLogger('remotepixel_api')
logger.setLevel(logging.INFO)


def response(status, content_type, response_body, cors=False):
    """
    Return HTTP response, including response code (status), headers and body
    """

    statusCode = {
        'OK': '200',
        'EMPTY': '204',
        'NOK': '400',
        'FOUND': '302',
        'NOT_FOUND': '404',
        'CONFLICT': '409',
        'ERROR': '500'}

    messageData = {
        'statusCode': statusCode[status],
        'body': response_body,
        'headers': {'Content-Type': content_type}}

    if cors:
        messageData['headers']['Access-Control-Allow-Origin'] = '*'
        messageData['headers']['Access-Control-Allow-Methods'] = 'GET,OPTIONS'

    if content_type in ['image/png', 'image/jpeg']:
        messageData['isBase64Encoded'] = True

    return messageData


def l8_overview_handler(event, context):
    """
    """
    logger.info(event)

    try:
        info = event.get('queryStringParameters')
        scene = info.get('scene')
        bands = info.get('bands', [4, 3, 2])
        bands = map(int, bands.split(',')) if isinstance(bands, str) else bands
        img_format = info.get('format', 'jpeg')

        if info.get('ndvi'):
            out = l8_ovr.create_ndvi(scene, img_format)
        else:
            out = l8_ovr.create(scene, bands, img_format)

        return response('OK', 'text/plain', out, True)

    except Exception as e:
        logger.error(e)
        return response('ERROR', 'application/json', json.dumps({'errorMessage': 'Error'}), True)


def l8_full_handler(event, context):
    """
    """
    logger.info(event)

    bucket = os.environ.get("OUTPUT_BUCKET")

    try:
        info = event.get('queryStringParameters')
        scene = info.get('scene')
        bands = info.get('bands', [4, 3, 2])
        bands = map(int, bands.split(',')) if isinstance(bands, str) else bands

        if info.get('ndvi'):
            l8_full.create_ndvi(scene, bucket)
            outfname = f'{scene}_NDVI.tif'
        else:
            l8_full.create(scene, bucket, bands)
            str_band = ''.join(map(str, bands))
            outfname = f'{scene}_B{str_band}.tif'

        out_url = f'https://s3-us-west-2.amazonaws.com/{bucket}/data/landsat/{outfname}'
        return response('OK', 'application/json', json.dumps({'path': out_url}), True)

    except Exception as e:
        logger.error(e)
        return response('ERROR', 'application/json', json.dumps({'errorMessage': 'Error'}), True)


def l8_ndvi_point_handler(event, context):
    """
    """
    logger.info(event)

    try:
        info = event.get('queryStringParameters')
        scene = info.get('scene')
        coords = info.get('coords')
        coords = eval(coords) if isinstance(coords, str) else coords

        out = l8_ndvi.point(scene, coords)

        return response('OK', 'application/json', json.dumps(out), True)

    except Exception as e:
        logger.error(e)
        return response('ERROR', 'application/json', json.dumps({'errorMessage': 'Error'}), True)


def l8_ndvi_area_handler(event, context):
    """
    """
    logger.info(event)

    try:
        info = event.get('queryStringParameters')
        scene = info.get('scene')
        bbox = info.get('bbox')
        bbox = eval(bbox) if isinstance(bbox, str) else bbox

        out = l8_ndvi.area(scene, bbox)
        return response('OK', 'text/plain', out, True)

    except Exception as e:
        logger.error(e)
        return response('ERROR', 'application/json', json.dumps({'errorMessage': 'Error'}), True)


def l8_mosaic_handler(event, context):
    """
    """
    logger.info(event)

    try:
        info = event.get('queryStringParameters')
        scenes = info.get('scenes')
        scenes = scenes.split(',') if isinstance(scenes, str) else scenes
        bands = info.get('bands', [4, 3, 2])
        bands = map(int, bands.split(',')) if isinstance(bands, str) else bands
        task_id = info.get('uuid', str(uuid.uuid1()))

        l8_mosaic.create(scenes, task_id, os.environ.get('OUTPUT_BUCKET'), bands)

        resp = {
            'uuid': task_id,
            'region': os.environ.get("AWS_REGION"),
            'bucket': os.environ.get("OUTPUT_BUCKET"),
            'tif': f'data/mosaic/{task_id}_mosaic.tif',
            'json': f'data/mosaic/{task_id}.json'}
        return response('OK', 'application/json', json.dumps(resp), True)

    except Exception as e:
        logger.error(e)
        return response('ERROR', 'application/json', json.dumps({'errorMessage': 'Error while creating the mosaic'}), True)


def srtm_mosaic_handler(event, context):
    '''
    '''
    logger.info(event)

    try:
        info = event.get('queryStringParameters')
        tiles = info.get('tiles')
        tiles = tiles.split(',') if isinstance(tiles, str) else tiles
        task_id = info.get('uuid', str(uuid.uuid1()))

        if len(tiles) > 8:
            return response('ERROR', 'application/json', json.dumps({'errorMessage': 'Tiles number > 8'}), True)

        srtm_mosaic.create(tiles, task_id, os.environ.get('OUTPUT_BUCKET'))

        resp = {
            'uuid': task_id,
            'region': os.environ.get("AWS_REGION"),
            'bucket': os.environ.get("OUTPUT_BUCKET"),
            'tif': f'data/srtm/{task_id}_mosaic.tif'}
        return response('OK', 'application/json', json.dumps(resp), True)

    except Exception as e:
        logger.error(e)
        return response('ERROR', 'application/json', json.dumps({'errorMessage': 'Error while creating the mosaic'}), True)


def s2_overview_handler(event, context):
    '''
    '''
    logger.info(event)

    try:
        info = event.get('queryStringParameters')
        scene = info.get('scene')
        bands = info.get('bands', ['04', '03', '02'])
        bands = bands.split(',') if isinstance(bands, str) else bands
        img_format = info.get('format', 'jpeg')

        ndvi = info.get('ndvi', None)
        if ndvi:
            out = s2_ovr.create_ndvi(scene, img_format)
        else:
            out = s2_ovr.create(scene, bands, img_format)

        return response('OK', 'text/plain', out, True)
    except Exception as e:
        logger.error(e)
        return response('ERROR', 'application/json', json.dumps({'errorMessage': 'Error'}), True)


def s2_full_handler(event, context):
    '''
    '''
    logger.info(event)

    bucket = os.environ.get("OUTPUT_BUCKET")

    try:
        info = event.get('queryStringParameters')
        scene = info.get('scene')
        bands = info.get('bands', ['04', '03', '02'])
        bands = bands.split(',') if isinstance(bands, str) else bands

        s2_full.create(scene, bucket, bands)
        str_band = ''.join(map(str, bands))
        outfname = f'{scene}_B{str_band}.tif'

        out_url = f'https://s3-us-west-2.amazonaws.com/{bucket}/data/landsat/{outfname}'
        return response('OK', 'application/json', json.dumps({'path': out_url}), True)

    except Exception as e:
        logger.error(e)
        return response('ERROR', 'application/json', json.dumps({'errorMessage': 'Error'}), True)
