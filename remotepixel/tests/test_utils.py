import pytest

import os
import io
import sys
import json

import numpy as np

from remotepixel import utils


mtl_file = os.path.join(os.path.dirname(__file__), 'fixtures', 'LC80140352017115LGN00_MTL.txt')
with open(mtl_file, 'r') as f:
    meta_data = f.read().splitlines()

def test_landsat_mtl_extract_valid():
    expectedContent = '37.08780'
    assert utils.landsat_mtl_extract(meta_data, 'CORNER_UL_LAT_PRODUCT') == expectedContent


def test_landsat_mtl_extract_Error():
    with pytest.raises(ValueError):
        utils.landsat_mtl_extract(meta_data, 'CORNER_UL_PRODUCT')

def test_linear_rescale_valid():
    data = np.zeros((1,1), dtype=np.uint16) + 1000
    expectedContent = np.zeros((1,1), dtype=np.uint16) + 25.5
    assert utils.linear_rescale(data, in_range=[0, 10000], out_range=[0, 255]) == expectedContent


def test_landsat_parse_scene_id_pre_invalid():
    scene = 'L0300342017083LGN00'
    with pytest.raises(ValueError):
        utils.landsat_parse_scene_id(scene)


def test_landsat_parse_scene_id_c1_invalid():
    scene = 'LC08_005004_20170410_20170414_01_T1'
    with pytest.raises(ValueError):
        utils.landsat_parse_scene_id(scene)


def test_landsat_parse_scene_id_pre_valid():
    scene = 'LC80300342017083LGN00'
    expectedContent = {
        'acquisitionJulianDay': '083',
        'acquisitionYear': '2017',
        'archiveVersion': '00',
        'date': '2017-03-24',
        'groundStationIdentifier': 'LGN',
        'key': 'L8/030/034/LC80300342017083LGN00/LC80300342017083LGN00',
        'path': '030',
        'row': '034',
        'satellite': '8',
        'scene': 'LC80300342017083LGN00',
        'sensor': 'C'
     }

    assert utils.landsat_parse_scene_id(scene) == expectedContent


def test_landsat_parse_scene_id_c1_valid():
    scene = 'LC08_L1TP_005004_20170410_20170414_01_T1'
    expectedContent = {
        'acquisitionDay': '10',
        'acquisitionMonth': '04',
        'acquisitionYear': '2017',
        'collectionCategory': 'T1',
        'collectionNumber': '01',
        'date': '2017-04-10',
        'key': 'c1/L8/005/004/LC08_L1TP_005004_20170410_20170414_01_T1/LC08_L1TP_005004_20170410_20170414_01_T1',
        'path': '005',
        'processingCorrectionLevel': 'L1TP',
        'processingDay': '14',
        'processingMonth': '04',
        'processingYear': '2017',
        'row': '004',
        'satellite': '08',
        'scene': 'LC08_L1TP_005004_20170410_20170414_01_T1',
        'sensor': 'C'
    }

    assert utils.landsat_parse_scene_id(scene) == expectedContent


def test_s2_parse_scene_id_invalid():
    scene = 'S2A_20170429_18TWR_0'
    with pytest.raises(ValueError):
        utils.sentinel_parse_scene_id(scene)


def test_s2_parse_scene_id_2A_valid():
    scene = 'S2A_tile_20170429_18TWR_0'
    expectedContent = {
        'sensor': '2',
        'satellite': 'A',
        'acquisitionYear': '2017',
        'acquisitionMonth': '04',
        'acquisitionDay': '29',
        'utm': '18',
        'sq': 'T',
        'lat': 'WR',
        'num': '0',
        'key': 'tiles/18/T/WR/2017/4/29/0'
    }

    assert utils.sentinel_parse_scene_id(scene) == expectedContent


def test_s2_parse_scene_id_2B_valid():
    scene = 'S2B_tile_20170429_18TWR_0'
    expectedContent = {
        'sensor': '2',
        'satellite': 'B',
        'acquisitionYear': '2017',
        'acquisitionMonth': '04',
        'acquisitionDay': '29',
        'utm': '18',
        'sq': 'T',
        'lat': 'WR',
        'num': '0',
        'key': 'tiles/18/T/WR/2017/4/29/0'
    }

    assert utils.sentinel_parse_scene_id(scene) == expectedContent
