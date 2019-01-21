"""app.elevation: handle SRTM requests."""

import os
import uuid

import boto3

from remotepixel import srtm_mosaic


def mosaic(event, context):
    """Handle mosaic requests."""
    bucket = os.environ["OUTPUT_BUCKET"]
    tiles = event.get('scenes')

    if len(tiles) > 8:
        raise Exception('8 tiles Maximum')

    mem = srtm_mosaic.mosaic(tiles)

    uid = str(uuid.uuid1())
    params = {
        'ACL': 'public-read',
        'Metadata': {
            'uuid': uid},
        'ContentType': 'image/tiff'}
    key = f'data/srtm/{uid}.tif'

    client = boto3.client('s3')
    client.upload_fileobj(mem, bucket, key, ExtraArgs=params)

    return {
        'path': f'https://s3.amazonaws.com/{bucket}/{key}'}


def wms(event, context):
    """Create WMTS xml."""
    return '''<GDAL_WMS>
    <Service name="TMS">
        <ServerUrl>http://elevation-tiles-prod.s3.amazonaws.com/geotiff/${z}/${x}/${y}.tif</ServerUrl>
    </Service>
    <DataWindow>
        <UpperLeftX>-20037508.34</UpperLeftX>
        <UpperLeftY>20037508.34</UpperLeftY>
        <LowerRightX>20037508.34</LowerRightX>
        <LowerRightY>-20037508.34</LowerRightY>
        <TileLevel>14</TileLevel>
        <TileCountX>1</TileCountX>
        <TileCountY>1</TileCountY>
        <YOrigin>top</YOrigin>
    </DataWindow>
    <ImageFormat>image/tif</ImageFormat>
    <DataType>UInt32</DataType>
    <Projection>EPSG:3857</Projection>
    <BlockSizeX>512</BlockSizeX>
    <BlockSizeY>512</BlockSizeY>
    <BandsCount>1</BandsCount>
    <MaxConnections>100</MaxConnections>
    <ZeroBlockOnServerException>true</ZeroBlockOnServerException>
</GDAL_WMS>'''
