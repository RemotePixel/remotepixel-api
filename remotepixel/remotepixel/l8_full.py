import os
import json

import boto3
import numpy as np

import rasterio as rio
from rasterio.io import MemoryFile
from rio_toa import reflectance

from remotepixel import utils

np.seterr(divide='ignore', invalid='ignore')

landsat_bucket = 's3://landsat-pds'

def create(scene, bucket, bands=[4,3,2]):
    """
    """

    scene_params = utils.landsat_parse_scene_id(scene)
    meta_data = utils.landsat_get_mtl(scene)
    landsat_address = f'{landsat_bucket}/{scene_params["key"]}'

    bqa = f'{landsat_address}_BQA.TIF'
    with rio.open(bqa) as src:
        meta = src.meta
        wind = [w for ij, w in src.block_windows(1)]

    meta.update(nodata=0, count=3, interleave='pixel',
        PHOTOMETRIC='RGB', tiled=False, compress=None)

    E = float(utils.landsat_mtl_extract(meta_data, 'SUN_ELEVATION'))

    with MemoryFile() as memfile:
        with memfile.open(**meta) as dataset:

            for b in range(len(bands)):
                band_address = f'{landsat_address}_B{bands[b]}.TIF'

                MR = float(utils.landsat_mtl_extract(meta_data,
                    f'REFLECTANCE_MULT_BAND_{bands[b]}'))
                AR = float(utils.landsat_mtl_extract(meta_data,
                    f'REFLECTANCE_ADD_BAND_{bands[b]}'))

                with rio.open(band_address) as src:
                    for window in wind:
                        matrix = src.read(
                            window=window, boundless=True, indexes=1)
                        result = reflectance.reflectance(
                            matrix, MR, AR, E, src_nodata=0) * 10000
                        dataset.write(result.astype(np.uint16),
                            window=window, indexes=b+1)

        client = boto3.client('s3')
        str_band = ''.join(map(str, bands))
        key = f'data/landsat/{scene}_B{str_band}.tif'
        response = client.put_object(
            ACL='public-read',
            Bucket=bucket,
            Key=key,
            Body=memfile,
            ContentType='image/tiff'
        )

    return True


##############################################################
def create_ndvi(scene, bucket):
    """
    """

    scene_params = utils.landsat_parse_scene_id(scene)
    meta_data = utils.landsat_get_mtl(scene)
    landsat_address = f'{landsat_bucket}/{scene_params["key"]}'

    bqa = f'{landsat_address}_BQA.TIF'
    with rio.open(bqa) as src:
        meta = src.meta
        wind = [w for ij, w in src.block_windows(1)]

    meta.update(nodata=0, count=1, interleave='pixel',
        tiled=False, compress=None, dtype=np.float32)

    E = float(utils.landsat_mtl_extract(meta_data, 'SUN_ELEVATION'))

    with MemoryFile() as memfile:
        with memfile.open(**meta) as dataset:

            band_address_b = f'{landsat_address}_B4.TIF'
            MR_B = float(utils.landsat_mtl_extract(meta_data,
                'REFLECTANCE_MULT_BAND_4'))
            AR_B = float(utils.landsat_mtl_extract(meta_data,
                'REFLECTANCE_ADD_BAND_4'))

            band_address_n = f'{landsat_address}_B5.TIF'
            MR_N = float(utils.landsat_mtl_extract(meta_data,
                'REFLECTANCE_MULT_BAND_5'))
            AR_N = float(utils.landsat_mtl_extract(meta_data,
                'REFLECTANCE_ADD_BAND_5'))

            with rio.open(band_address_b) as b4:
                with rio.open(band_address_n) as b5:
                    for window in wind:
                        matrix = b4.read(window=window, boundless=True,
                            indexes=1)
                        b4_data = reflectance.reflectance(
                            matrix, MR_B, AR_B, E, src_nodata=0)

                        matrix = b5.read(window=window, boundless=True,
                            indexes=1)
                        b5_data = reflectance.reflectance(
                            matrix, MR_N, AR_N, E, src_nodata=0)

                        ratio = np.where((b5_data * b4_data) > 0,
                            np.nan_to_num(
                                (b5_data - b4_data) / (b5_data + b4_data)), -1)

                        dataset.write(ratio, window=window, indexes=1)

        client = boto3.client('s3')
        key = f'data/landsat/{scene}_NDVI.tif'
        response = client.put_object(
            ACL='public-read',
            Bucket=bucket,
            Key=key,
            Body=memfile,
            ContentType='image/tiff'
        )

    return True
