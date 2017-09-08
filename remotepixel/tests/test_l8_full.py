import pytest

import os
import io
import sys
import json
import pytest

from mock import patch

from remotepixel import l8_full

landsat_scene_c1 = 'LC08_L1TP_016037_20170813_20170814_01_RT'
landsat_bucket = os.path.join(os.path.dirname(__file__), 'fixtures', 'landsat-pds')

landsat_path = os.path.join(landsat_bucket,
    'c1', 'L8', '016', '037', landsat_scene_c1, landsat_scene_c1)
with open(f'{landsat_path}_MTL.txt', 'r') as f:
    landsat_meta = f.read().splitlines()


@patch('remotepixel.l8_full.boto3.client')
@patch('remotepixel.utils.landsat_get_mtl')
def test_create_valid(landsat_get_mtl, client, monkeypatch):
    """
    Should work as expected (read data, create RGB and upload to S3)
    """

    monkeypatch.setattr(l8_full, 'landsat_bucket', landsat_bucket)
    landsat_get_mtl.return_value = landsat_meta
    client.return_value.put_object.return_value = True

    bucket = 'my-bucket'
    assert l8_full.create(landsat_scene_c1, bucket)


@patch('remotepixel.l8_full.boto3.client')
@patch('remotepixel.utils.landsat_get_mtl')
def test_create_validBands(landsat_get_mtl, client, monkeypatch):
    """
    Should work as expected (read data, create RGB and upload to S3)
    """

    monkeypatch.setattr(l8_full, 'landsat_bucket', landsat_bucket)
    landsat_get_mtl.return_value = landsat_meta
    client.return_value.put_object.return_value = True

    bucket = 'my-bucket'
    bands = [5,4,3]
    assert l8_full.create(landsat_scene_c1, bucket, bands)


@patch('remotepixel.l8_full.boto3.client')
@patch('remotepixel.utils.landsat_get_mtl')
def test_create_valid(landsat_get_mtl, client, monkeypatch):
    """
    Should work as expected (read data, create NDVI and upload to S3)
    """

    monkeypatch.setattr(l8_full, 'landsat_bucket', landsat_bucket)
    landsat_get_mtl.return_value = landsat_meta
    client.return_value.put_object.return_value = True

    bucket = 'my-bucket'
    assert l8_full.create_ndvi(landsat_scene_c1, bucket)
