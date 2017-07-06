# remotepixel-api
Process Landsat and Sentinel data using AWS Lambda functions

=========

### What this is

Serverless architecture powering most of [remotepixel.ca](https://remotepixel.ca/) cloud processing projects (e.g [Landsat full resolution donwload in satellitesearch](https://remotepixel.ca/blog/landsat-full-resolution-in-satellitesearch_20161006.html)).

#### Python 3.6 + Rasterio + AWS Lambda + API gateway
`# TO DO`

### How to
`# TO DO`

### Requierement
  - AWS Account
  - awscli
  - Docker
  - npm


### Creating and deploy

⚠️ ⚠️ ⚠️
You need to update `OUTPUT BUCKET` value in https://github.com/RemotePixel/remotepixel-api/blob/master/serverless.yml ([here](https://github.com/RemotePixel/remotepixel-api/blob/654d98b0b5ea7ee21c8e343573e049e026595cf6/serverless.yml#L19) and [here](https://github.com/RemotePixel/remotepixel-api/blob/654d98b0b5ea7ee21c8e343573e049e026595cf6/serverless.yml#L40))

```
make build && make package

npm install -g serverless

make deploy-us && make deploy-eu
```

#### Why us & eu ?
Landsat and SRTM data are hosted in **us-west-2** region while Sentinel data are in **eu-central-1**. By deploying twice in `us-west-2`  and in `eu-central-1` we can have Landsat and Sentinel functions running as close as possible to the data. Make sure to call the good endpoint when working with sentinel (`execute-api.eu-central-1.amazonaws.com`) and Landsat (`execute-api.us-west-2.amazonaws.com`).

### functions

- [l8_overview](https://github.com/RemotePixel/remotepixel-api#l8_overview)
- [l8_full](https://github.com/RemotePixel/remotepixel-api#l8_full)
- [l8_ndvi_point](https://github.com/RemotePixel/remotepixel-api#l8_ndvi_point)
- [l8_ndvi_area](https://github.com/RemotePixel/remotepixel-api#l8_ndvi_area)
- [l8_mosaic](https://github.com/RemotePixel/remotepixel-api#l8_mosaic)
- [srtm_mosaic](https://github.com/RemotePixel/remotepixel-api#srtm_mosaic)
- [s2_overview](https://github.com/RemotePixel/remotepixel-api#s2_overview)


## l8_overview

Create Landsat 8 overview rgb.

input:
- **scene**: Landsat scene id
- **bands**: array of band number (default: `[4,3,2]`) [OPTION]
- **format**: image format (`jpeg` or `png`) [OPTION]

return:
- base64 encoded rgb image

Example:

```bash
$ curl "https://{API}.execute-api.us-west-2.amazonaws.com/production/l8_overview?scene=LC08_L1TP_013030_20170520_20170520_01_RT&bands=5,4,2"

/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAA....
```

## l8_full

Create Landsat 8 full resolution rgb and save it to a S3 bucket.

input:
- **scene**: Landsat scene id
- **bands**: array of band number (default: `[4,3,2]`) [OPTION]

return:
- JSON object with AWS S3 path of the file

Example:

```bash
$ curl "https://{API}.execute-api.us-west-2.amazonaws.com/production/l8_full?scene=LC08_L1TP_013030_20170520_20170520_01_RT&bands=5,4,2"

{"path": "https://{s3-us-west-2}.amazonaws.com/{my-bucket}/data/landsat/LC08_L1TP_013030_20170520_20170520_01_RT_B542.tif"}
```

## l8_ndvi_point

Get NDVI value for a point and a landsat scene id.

input:
- **scene**: Landsat scene id
- **coords**: WGS84 lon,lat array

return:
- JSON object with ndvi value, cloud % and date

Example:

```bash
$ curl "https://{API}.execute-api.us-west-2.amazonaws.com/production/l8_ndvi_point?scene=LC08_L1TP_013030_20170520_20170520_01_RT&coords=-72,43"
{"ndvi": 0.7301119622863878, "date": "2017-05-20", "cloud": 0.01}
```

## l8_ndvi_area

Get NDVI image for a bbox and a landsat scene id.

input:
- **scene**: Landsat scene id
- **bbox**: WGS84 bounding box

return:
- base64 encoded rgb image

Example:

```bash
$ curl "https://{API}.execute-api.us-west-2.amazonaws.com/production/l8_ndvi_area?scene=LC08_L1TP_013030_20170520_20170520_01_RT&bbox=-73,42,-71,43"

/9j/4AAQSkZJRgABAQAAAQABAAD/...
```

## l8_mosaic

Create Landsat 8 overview mosaic

input:
- **scenes**: Landsat scene id list
- **bands**: array of band number (default: `[4,3,2]`) [OPTION]

return:
- JSON object with mosaic unique id (`uuid`) and S3 info

Example:

```bash
$ curl "https://{API}.execute-api.us-west-2.amazonaws.com/production/l8_mosaic?scenes=LC08_L1TP_016038_20170610_20170627_01_T1,LC08_L1TP_017038_20170516_20170525_01_T1,LC08_L1TP_017037_20170516_20170525_01_T1&bands=-5,4,3"

{
    'uuid': '00000000000000000000',
    'region': 'us-west-2',
    'bucket': 'my-bucket',
    'tif': 'data/mosaic/00000000000000000000_mosaic.tif',
    'json': 'data/mosaic/00000000000000000000.json'
}
```

## srtm_mosaic

Create SRTM 1arc mosaic

input:
- **tiles**: list of SRTM tiles

return:
- JSON object with mosaic unique id (`uuid`) and S3 info

Example:

```bash
$ curl "https://{API}.execute-api.us-west-2.amazonaws.com/production/srtm_mosaic?tiles=N41W007,N41W006,N41W005,N40W007,N40W006,N40W005"

{
    'uuid': '00000000000000000000',
    'region': 'us-west-2',
    'bucket': 'my-bucket',
    'tif': 'data/srtm/00000000000000000000.tif',
}
```


## s2_overview

Create Sentinel 2 overview rgb.

input:
- **scene**: Sentinel scene id
- **bands**: array of band number (default: `[4,3,2]`) [OPTION]
- **format**: image format (`jpeg` or `png`) [OPTION]

return:
- base64 encoded rgb image

Example:

```bash
$ curl "https://{API}.execute-api.eu-central-1.amazonaws.com/production/s2_overview?scene=S2A_tile_20170526_18SUF_0&bands=08,04,03"

/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAA....
```
