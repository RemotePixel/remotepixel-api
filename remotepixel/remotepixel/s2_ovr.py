import json
import base64
from io import BytesIO
from concurrent import futures

import numpy as np
from PIL import Image

import rasterio as rio
from rasterio.enums import Resampling

from remotepixel import utils

np.seterr(divide='ignore', invalid='ignore')

sentinel_bucket = 's3://sentinel-s2-l1c'

# https://en.wikipedia.org/wiki/Sentinel-2
band_info = {
    '01': { 'res': 60, 'wavelenght': 0.443, 'name': 'Coastal aerosol' },
    '02': { 'res': 10, 'wavelenght': 0.490, 'name': 'Blue' },
    '03': { 'res': 10, 'wavelenght': 0.560, 'name': 'Green' },
    '04': { 'res': 10, 'wavelenght': 0.665, 'name': 'Red' },
    '05': { 'res': 20, 'wavelenght': 0.705, 'name': 'Vegetation Red Edge' },
    '06': { 'res': 20, 'wavelenght': 0.740, 'name': 'Vegetation Red Edge' },
    '07': { 'res': 20, 'wavelenght': 0.783, 'name': 'Vegetation Red Edge' },
    '08': { 'res': 10, 'wavelenght': 0.842, 'name': 'NIR' },
    '8A': { 'res': 20, 'wavelenght': 0.865, 'name': 'Vegetation Red Edge' },
    '09': { 'res': 60, 'wavelenght': 0.945, 'name': 'Water vapour' },
    '10': { 'res': 60, 'wavelenght': 1.375, 'name': 'SWIR' },
    '11': { 'res': 20, 'wavelenght': 1.610, 'name': 'SWIR' },
    '12': { 'res': 20, 'wavelenght': 2.190, 'name': 'SWIR' }
}


def worker(args):
    """
    """
    address, ovrSize = args

    with rio.open(address) as src:
        matrix = src.read(indexes=1,
            out_shape=(ovrSize, ovrSize),
            resampling=Resampling.bilinear).astype(src.profile['dtype'])

        imgRange = np.percentile(matrix[matrix > 0], (2, 98)).tolist()
        matrix = np.where(matrix > 0,
            utils.linear_rescale(matrix,
            in_range=imgRange, out_range=[1, 255]), 0).astype(np.uint8)

        return matrix


def create(scene, bands=['04','03','02'], img_format='jpeg', ovrSize=512):
    """
    """

    if img_format not in ['png', 'jpeg']:
        raise UserWarning(f'Invalid {img_format} extension')

    scene_params = utils.sentinel_parse_scene_id(scene)
    sentinel_address = f'{sentinel_bucket}/{scene_params["key"]}'

    args = ((f'{sentinel_address}/B{band}.jp2', ovrSize) for band in bands)

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

    scene_params = utils.sentinel_parse_scene_id(scene)
    sentinel_address = f'{sentinel_bucket}/{scene_params["key"]}'

    bands = ['08','04']
    args = ((f'{sentinel_address}/B{band}.jp2', ovrSize) for band in bands)

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        out = list(executor.map(worker, args))

    ratio = np.where((out[1] * out[0]) > 0,
        np.nan_to_num((out[1] - out[0]) / (out[1] + out[0])), -1)
    ratio = np.where(ratio > -1,
        utils.linear_rescale(ratio, in_range=[-1,1],
            out_range=[1, 255]), 0).astype(np.uint8)

    cmap = list(np.array(utils.getColorMap()).flatten())
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
