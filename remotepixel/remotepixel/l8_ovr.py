import json
import base64
from io import BytesIO
from concurrent import futures

import numpy as np
from PIL import Image

import rasterio as rio
from rasterio.enums import Resampling
from rio_toa import reflectance

from remotepixel import utils

def create(scene, bands=[4,3,2], img_format='jpeg', ovrSize=512):

    def worker(args):

        address, band, meta = args

        MR = float(utils.landsat_mtl_extract(meta, f'REFLECTANCE_MULT_BAND_{band}'))
        AR = float(utils.landsat_mtl_extract(meta, f'REFLECTANCE_ADD_BAND_{band}'))
        E = float(utils.landsat_mtl_extract(meta, 'SUN_ELEVATION'))

        with rio.open(address) as src:
            matrix = src.read(indexes=1,
                out_shape=(ovrSize, ovrSize),
                resampling=Resampling.bilinear).astype(src.profile['dtype'])

            matrix = reflectance.reflectance(matrix, MR, AR, E, src_nodata=0) * 10000
            imgRange = np.percentile(matrix[matrix > 0], (2, 98)).tolist()

            matrix = np.where(matrix > 0,
                utils.linear_rescale(matrix,
                in_range=imgRange, out_range=[1, 255]), 0).astype(np.uint8)

            return matrix


    if img_format not in ['png', 'jpeg']:
        raise UserWarning(f'Invalid {img_format} extension')

    scene_params = utils.landsat_parse_scene_id(scene)
    meta_data = utils.landsat_get_mtl(scene)
    landsat_address = f's3://landsat-pds/{scene_params["key"]}'

    args = ((f'{landsat_address}_B{band}.TIF', band, meta_data)
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
