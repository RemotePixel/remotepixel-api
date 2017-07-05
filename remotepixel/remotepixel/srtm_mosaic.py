import os
import json
import zlib
import boto3
from concurrent import futures

import numpy as np

import rasterio as rio
from rasterio.merge import merge
from rasterio.io import MemoryFile

from urllib.request import urlopen

srtm_site = 'https://s3.amazonaws.com/elevation-tiles-prod/skadi'

def create(tiles, uuid, bucket):
    '''
    '''

    def worker(tile):
        '''
        '''

        try:
            outpath = f'/tmp/{tile}.hgt'
            url = f'{srtm_site}/{tile[0:3]}/{tile}.hgt.gz'
            with open(outpath, 'wb') as f:
                f.write(zlib.decompress(urlopen(url).read(), zlib.MAX_WBITS|16))
            return outpath
        except:
            return None


    if len(tiles) > 8:
        return False

    with futures.ThreadPoolExecutor(max_workers=8) as executor:
        responses = list(executor.map(worker, tiles))

    sources = [ rio.open(tile) for tile in responses if tile ]
    dest, output_transform = merge(sources, nodata=-32767)

    with MemoryFile() as memfile:
        with memfile.open(driver='GTiff',
            count=1, dtype=np.int16, nodata=-32767,
            height=dest.shape[1], width=dest.shape[2],
            compress='DEFLATE',
            crs='epsg:4326', transform=output_transform) as dataset:
            dataset.write(dest)

        client = boto3.client('s3')
        response = client.put_object(
            ACL='public-read',
            Bucket=bucket,
            Key=os.path.join('data', 'srtm', '{}.tif'.format(uuid)),
            Body=memfile,
            ContentType='image/tiff'
        )

    return True
