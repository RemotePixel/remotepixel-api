
SHELL = /bin/bash

all: build package


build:
	docker build -f Dockerfile --tag remotepixel:latest .

run:
	docker run \
		-w /var/task/ \
		--name remotepixel \
		--env AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
		--env AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
		--env AWS_REGION=us-west-2 \
		--env PYTHONPATH=/var/task/vendored \
		--env GDAL_DATA=/var/task/share/gdal \
		--env GDAL_CACHEMAX=75% \
		--env GDAL_DISABLE_READDIR_ON_OPEN=TRUE \
		--env GDAL_TIFF_OVR_BLOCKSIZE=512 \
		--env VSI_CACHE=TRUE \
		--env VSI_CACHE_SIZE=20000000 \
		-itd \
		remotepixel:latest


package:
	docker run \
		-w /var/task/ \
		--name remotepixel \
		-itd \
		remotepixel:latest
	docker cp remotepixel:/tmp/package.zip package.zip
	docker stop remotepixel
	docker rm remotepixel


shell:
	docker run \
		--name remotepixel  \
		--volume $(shell pwd)/:/data \
		--env AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
		--env AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
		--env AWS_REGION=us-west-2 \
		--env PYTHONPATH=/var/task/vendored \
		--env GDAL_DATA=/var/task/share/gdal \
		--env GDAL_CACHEMAX=75% \
		--env GDAL_DISABLE_READDIR_ON_OPEN=TRUE \
		--env GDAL_TIFF_OVR_BLOCKSIZE=512 \
		--env VSI_CACHE=TRUE \
		--env VSI_CACHE_SIZE=20000000 \
		--rm \
		-it \
		remotepixel:latest /bin/bash


deploy-us:
	sls deploy --region us-west-2


deploy-eu:
	sls deploy --region eu-central-1


clean:
	docker stop remotepixel
	docker rm remotepixel
