import pytest

import os
import io
import sys
import json
import pytest

from mock import patch

from remotepixel import l8_ndvi

landsat_scene_c1 = 'LC08_L1TP_016037_20170813_20170814_01_RT'
landsat_bucket = os.path.join(os.path.dirname(__file__), 'fixtures', 'landsat-pds')

landsat_path = os.path.join(landsat_bucket,
    'c1', 'L8', '016', '037', landsat_scene_c1, landsat_scene_c1)
with open(f'{landsat_path}_MTL.txt', 'r') as f:
    landsat_meta = f.read().splitlines()


@patch('remotepixel.utils.landsat_get_mtl')
def test_point_valid(landsat_get_mtl, monkeypatch):
    """
    Should work as expected (read data, calculate NDVI and return json info)
    """

    monkeypatch.setattr(l8_ndvi, 'landsat_bucket', landsat_bucket)
    landsat_get_mtl.return_value = landsat_meta

    coords = [-80.073, 33.17]
    expectedContent = {
        "cloud": 26.70,
        "date": '2017-08-13',
        "ndvi": 0.7174432277679443
    }

    assert l8_ndvi.point(landsat_scene_c1, coords) == expectedContent


@patch('remotepixel.utils.landsat_get_mtl')
def test_point_validZero(landsat_get_mtl, monkeypatch):
    """
    Should work as expected (read data, calculate NDVI and return json info)
    """

    monkeypatch.setattr(l8_ndvi, 'landsat_bucket', landsat_bucket)
    landsat_get_mtl.return_value = landsat_meta

    coords = [-80.0, 32.1]
    expectedContent = {
        "cloud": 26.70,
        "date": '2017-08-13',
        "ndvi": 0.
    }

    assert l8_ndvi.point(landsat_scene_c1, coords) == expectedContent


@patch('remotepixel.utils.landsat_get_mtl')
def test_area_valid(landsat_get_mtl, monkeypatch):
    """
    Should work as expected (read data, calculate NDVI and return img)
    """

    monkeypatch.setattr(l8_ndvi, 'landsat_bucket', landsat_bucket)
    landsat_get_mtl.return_value = landsat_meta

    bbox = [-80.5, 32.5, -79.5, 33.5]
    
    assert l8_ndvi.area(landsat_scene_c1, bbox)
