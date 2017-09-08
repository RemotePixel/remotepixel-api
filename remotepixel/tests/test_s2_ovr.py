import pytest

import os
import io
import sys
import json
import pytest

from mock import patch

from remotepixel import s2_ovr

sentinel_scene = 'S2A_tile_20170729_19UDP_0'
sentinel_bucket = os.path.join(os.path.dirname(__file__), 'fixtures', 'sentinel-s2-l1c')
sentinel_path = os.path.join(sentinel_bucket, 'tiles/19/U/DP/2017/7/29/0/')

def test_worker_valid():
    """
    Should work as expected (read data, and rescale to int)
    """

    address = f'{sentinel_path}/B04.jp2'

    assert s2_ovr.worker((address, 512, False)).shape == (512, 512)


def test_worker_validNdvi():
    """
    Should work as expected (read data)
    """

    address = f'{sentinel_path}/B04.jp2'

    assert s2_ovr.worker((address, 512, True)).shape == (512, 512)


def test_create_valid(monkeypatch):
    """
    Should work as expected (read r,g,b bands and create JPEG image)
    """

    monkeypatch.setattr(s2_ovr, 'sentinel_bucket', sentinel_bucket)

    assert s2_ovr.create(sentinel_scene, bands=['04','03','02'])


def test_create_validPNG(monkeypatch):
    """
    Should work as expected (read r,g,b bands and create PNG image)
    """

    monkeypatch.setattr(s2_ovr, 'sentinel_bucket', sentinel_bucket)

    assert s2_ovr.create(sentinel_scene, bands=['04','03','02'], img_format='png')


def test_create_validSmall(monkeypatch):
    """
    Should work as expected (read bands and create 128x128 image)
    """

    monkeypatch.setattr(s2_ovr, 'sentinel_bucket', sentinel_bucket)

    assert s2_ovr.create(sentinel_scene, bands=['04','03','02'], ovrSize=128)


def test_create_validdefault(monkeypatch):
    """
    Should work as expected (read bands and create 128x128 image)
    """

    monkeypatch.setattr(s2_ovr, 'sentinel_bucket', sentinel_bucket)

    assert s2_ovr.create(sentinel_scene, ovrSize=128)


def test_create_invalidFormat(monkeypatch):
    """
    Should raise invalid format
    """

    monkeypatch.setattr(s2_ovr, 'sentinel_bucket', sentinel_bucket)

    with pytest.raises(UserWarning):
        s2_ovr.create(sentinel_scene, img_format='tif')


def test_create_ndvi_valid(monkeypatch):
    """
    Should work as expected (read nir and red bands and create PNG image)
    """

    monkeypatch.setattr(s2_ovr, 'sentinel_bucket', sentinel_bucket)

    assert s2_ovr.create_ndvi(sentinel_scene)


def test_create_ndvi_validPNG(monkeypatch):
    """
    Should work as expected (read nir and red bands and create PNG image)
    """

    monkeypatch.setattr(s2_ovr, 'sentinel_bucket', sentinel_bucket)

    assert s2_ovr.create_ndvi(sentinel_scene, img_format='png')


def test_create_ndvi_validSmall(monkeypatch):
    """
    Should work as expected (read bands and create 128x128 image)
    """

    monkeypatch.setattr(s2_ovr, 'sentinel_bucket', sentinel_bucket)

    assert s2_ovr.create_ndvi(sentinel_scene, ovrSize=128)


def test_create_ndvi_invalidFormat(monkeypatch):
    """
    Should raise invalid format
    """

    monkeypatch.setattr(s2_ovr, 'sentinel_bucket', sentinel_bucket)


    with pytest.raises(UserWarning):
        s2_ovr.create_ndvi(sentinel_scene, img_format='tif')
