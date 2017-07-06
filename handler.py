
import os
import json
import uuid
import logging

from remotepixel import l8_ovr, l8_full, l8_mosaic, l8_ndvi, srtm_mosaic, s2_ovr

logger = logging.getLogger('remotepixel_api')
logger.setLevel(logging.INFO)


def response(status, content_type, response_body, cors=False):
    '''
    Return HTTP response, including response code (status), headers and body
    '''

    statusCode = {
        'OK': '200',
        'EMPTY': '204',
        'NOK': '400',
        'FOUND': '302',
        'NOT_FOUND': '404',
        'CONFLICT': '409',
        'ERROR': '500'
    }
    messageData = {
        'statusCode': statusCode[status],
        'body': response_body,
        'headers': {
            'Content-Type': content_type
        }
    }

    if cors:
        messageData['headers']['Access-Control-Allow-Origin'] = '*'
        messageData['headers']['Access-Control-Allow-Methods'] = 'GET,POST'

    if content_type in ['image/png', 'image/jpeg']:
        messageData['isBase64Encoded'] = True

    return messageData


def l8_overview_handler(event, context):
    '''
    '''
    logger.info(event)

    try:
        info = event.get('queryStringParameters')
        scene = info.get('scene')
        bands = info.get('bands', [4,3,2])
        bands = eval(bands) if isinstance(bands, str) else bands
        img_format = info.get('format', 'jpeg')

        out = l8_ovr.create(scene, bands, img_format)
        return response('OK', 'text/plain', out, True)
    except:
        return response('ERROR', 'application/json', json.dumps({'ErrorMessage': 'Error'}), True)


def l8_full_handler(event, context):
    '''
    '''
    logger.info(event)

    try:
        info = event.get('queryStringParameters')
        scene = info.get('scene')
        bands = info.get('bands', [4,3,2])
        bands = eval(bands) if isinstance(bands, str) else bands

        out = l8_full.create(scene, os.environ.get('OUTPUT_BUCKET'), bands)

        str_band = ''.join(map(str, bands))
        return response('OK',
            'application/json',
            json.dumps({ 'path': f'https://s3-us-west-2.amazonaws.com/{os.environ.get("OUTPUT_BUCKET")}/data/landsat/{scene}_B{str_band}.tif'}), True)
    except:
        return response('ERROR', 'application/json', json.dumps({'ErrorMessage': 'Error'}), True)


def l8_ndvi_point_handler(event, context):
    '''
    '''
    logger.info(event)

    try:
        info = event.get('queryStringParameters')
        scene = info.get('scene')
        coords = info.get('coords')
        coords = eval(coords) if isinstance(coords, str) else coords

        out = l8_ndvi.point(scene, coords)
        return response('OK', 'application/json', json.dumps(out), True)
    except:
        return response('ERROR', 'application/json', json.dumps({'ErrorMessage': 'Error'}), True)


def l8_ndvi_area_handler(event, context):
    '''
    '''
    logger.info(event)

    try:
        info = event.get('queryStringParameters')
        scene = info.get('scene')
        bbox = info.get('bbox')
        bbox = eval(bbox) if isinstance(bbox, str) else bbox

        out = l8_ndvi.area(scene, bbox)
        return response('OK', 'text/plain', out, True)
    except:
        return response('ERROR', 'application/json', json.dumps({'ErrorMessage': 'Error'}), True)


def l8_mosaic_handler(event, context):
    '''
    '''
    logger.info(event)

    try:
        info = event.get('queryStringParameters')
        scenes = info.get('scenes')
        scenes = scenes.split(',') if isinstance(scenes, str) else scenes
        bands = info.get('bands', [4,3,2])
        bands = eval(bands) if isinstance(bands, str) else bands
        task_id = info.get('uuid', str(uuid.uuid1()))

        out = l8_mosaic.create(scenes, task_id, os.environ.get('OUTPUT_BUCKET'), bands)

        s3_path = f's3://{os.environ.get("OUTPUT_BUCKET")}/data/srtm/{task_id}.tif'
        url = f'https://s3-us-west-2.amazonaws.com/{os.environ.get("OUTPUT_BUCKET")}/data/srtm/{task_id}.tif'

        resp = {
            'uuid': task_id,
            'region': os.environ.get("AWS_REGION"),
            'bucket': os.environ.get("OUTPUT_BUCKET"),
            'tif': f'data/mosaic/{task_id}_mosaic.tif',
            'json': f'data/mosaic/{task_id}.json'
        }
        return response('OK', 'application/json', json.dumps(resp), True)
    except:
        return response('ERROR', 'application/json', json.dumps({'ErrorMessage': 'Error while creating the mosaic'}), True)


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
            return response('ERROR', 'application/json', json.dumps({'ErrorMessage': 'Tiles number > 8'}), True)

        out = srtm_mosaic.create(tiles, task_id, os.environ.get('OUTPUT_BUCKET'))

        resp = {
            'uuid': task_id,
            'region': os.environ.get("AWS_REGION"),
            'bucket': os.environ.get("OUTPUT_BUCKET"),
            'tif': f'data/srtm/{task_id}_mosaic.tif'
        }
        return response('OK', 'application/json', json.dumps(resp), True)
    except:
        return response('ERROR', 'application/json', json.dumps({'ErrorMessage': 'Error while creating the mosaic'}), True)


def s2_overview_handler(event, context):
    '''
    '''
    logger.info(event)

    try:
        info = event.get('queryStringParameters')
        scene = info.get('scene')
        bands = info.get('bands', ['04','03','02'])
        bands = bands.split(',') if isinstance(bands, str) else bands
        img_format = info.get('format', 'jpeg')

        out = s2_ovr.create(scene, bands, img_format)
        return response('OK', 'text/plain', out, True)
    except:
        return response('ERROR', 'application/json', json.dumps({'ErrorMessage': 'Error'}), True)
