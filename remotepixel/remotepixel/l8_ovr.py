import json
import base64
from io import BytesIO
from concurrent import futures

import numpy as np
from PIL import Image

from rio_toa import reflectance

from remotepixel import utils

np.seterr(divide='ignore', invalid='ignore')

landsat_bucket = 's3://landsat-pds'


def worker(args):
    """
    """

    address, band, meta, ovrSize, ndvi = args

    MR = float(utils.landsat_mtl_extract(meta, f'REFLECTANCE_MULT_BAND_{band}'))
    AR = float(utils.landsat_mtl_extract(meta, f'REFLECTANCE_ADD_BAND_{band}'))
    E = float(utils.landsat_mtl_extract(meta, 'SUN_ELEVATION'))

    matrix = utils.get_overview(address, ovrSize)
    matrix = reflectance.reflectance(matrix, MR, AR, E, src_nodata=0)
    if not ndvi:
        imgRange = np.percentile(matrix[matrix > 0], (2, 98)).tolist()
        matrix = np.where(matrix > 0,
            utils.linear_rescale(matrix,
            in_range=imgRange, out_range=[1, 255]), 0).astype(np.uint8)

    return matrix


def create(scene, bands=[4,3,2], img_format='jpeg', ovrSize=512):
    """
    """

    if img_format not in ['png', 'jpeg']:
        raise UserWarning(f'Invalid {img_format} extension')

    scene_params = utils.landsat_parse_scene_id(scene)
    meta_data = utils.landsat_get_mtl(scene)
    landsat_address = f'{landsat_bucket}/{scene_params["key"]}'

    args = ((f'{landsat_address}_B{band}.TIF', band, meta_data, ovrSize, False)
        for band in bands)

    out = np.zeros((4, ovrSize, ovrSize), dtype=np.uint8)
    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        out[0:3] = list(executor.map(worker, args))

    out[-1] = np.all(np.dstack(out[:3]) != 0, axis=2).astype(np.uint8) * 255

    img = Image.fromarray(np.dstack(out))
    sio = BytesIO()

    if img_format == 'jpeg':
        img = img.convert('RGB')
        img.save(sio, 'jpeg', subsampling=0, quality=100)
    else:
        img.save(sio, 'png', compress_level=0)

    sio.seek(0)

    return base64.b64encode(sio.getvalue()).decode()


def create_ndvi(scene, img_format='jpeg', ovrSize=512):
    """
    """

    if img_format not in ['png', 'jpeg']:
        raise UserWarning(f'Invalid {img_format} extension')

    scene_params = utils.landsat_parse_scene_id(scene)
    meta_data = utils.landsat_get_mtl(scene)
    landsat_address = f'{landsat_bucket}/{scene_params["key"]}'

    bands = [4,5]

    args = ((f'{landsat_address}_B{band}.TIF', band, meta_data, ovrSize, True)
        for band in bands)

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        out = list(executor.map(worker, args))

    ratio = np.where((out[1] * out[0]) > 0,
        np.nan_to_num((out[1] - out[0]) / (out[1] + out[0])), -1)

    ratio = np.where(ratio > -1,
        utils.linear_rescale(ratio, in_range=[-1,1],
            out_range=[1, 255]), 0).astype(np.uint8)

    cmap = list(np.array(utils.get_colormap()).flatten())
    img = Image.fromarray(ratio, 'P')
    img.putpalette(cmap)

    sio = BytesIO()
    if img_format == 'jpeg':
        img = img.convert('RGB')
        img.save(sio, 'jpeg', subsampling=0, quality=100)
    else:
        img.save(sio, 'png', compress_level=0)

    sio.seek(0)

    return base64.b64encode(sio.getvalue()).decode()
