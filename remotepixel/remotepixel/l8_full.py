import os
import json
import concurrent

import boto3
import numpy as np

import rasterio as rio
from rasterio.io import MemoryFile

from remotepixel import utils

##############################################################
def create(scene, bucket, bands=[4,3,2]):

    def worker(window, address):
        with rio.open(address) as src:
            return src.read(window=window, boundless=True, indexes=1)

    scene_params = utils.landsat_parse_scene_id(scene)
    meta_data = utils.landsat_get_mtl(scene)
    landsat_address = f's3://landsat-pds/{scene_params["key"]}'

    bqa = f'{landsat_address}_BQA.TIF'
    with rio.open(bqa) as src:
        meta = src.meta
        wind = [w for ij, w in src.block_windows(1)]

    meta.update(nodata=0, count=3, interleave='pixel',
        PHOTOMETRIC='RGB', tiled=False, compress=None)

    with MemoryFile() as memfile:
        with memfile.open(**meta) as dataset:

            for b in range(len(bands)):
                band_address = f'{landsat_address}_B{bands[b]}.TIF'

                with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                    future_to_window = {
                        executor.submit(worker, window, band_address): window
                            for window in wind}

                    for future in concurrent.futures.as_completed(future_to_window):
                        window = future_to_window[future]
                        result = utils.landsat_to_toa(future.result(), bands[b], meta_data)
                        dataset.write(result, indexes=b+1, window=window)

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
