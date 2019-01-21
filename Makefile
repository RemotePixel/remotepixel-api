
SHELL = /bin/bash

package:
	docker build --tag remotepixelapi:latest .
	docker run --name remotepixelapi -itd remotepixelapi:latest /bin/bash
	docker cp remotepixelapi:/tmp/package.zip package.zip
	docker stop remotepixelapi
	docker rm remotepixelapi

test:
	docker build --tag remotepixelapi:latest .
	docker run \
		-w /var/task/ \
		--name remotepixelapi \
		--env AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
		--env AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
 		--env AWS_REGION=us-west-2 \
		--env PYTHONPATH=/var/task \
		--env GDAL_DATA=/var/task/share/gdal \
	  --env GDAL_CACHEMAX=75% \
	  --env VSI_CACHE=TRUE \
	  --env VSI_CACHE_SIZE=536870912 \
	  --env CPL_TMPDIR="/tmp" \
	  --env GDAL_HTTP_MERGE_CONSECUTIVE_RANGES=YES \
		--env GDAL_HTTP_MULTIPLEX=YES \
	  --env GDAL_HTTP_VERSION=2 \
	  --env GDAL_DISABLE_READDIR_ON_OPEN=TRUE \
	  --env CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".TIF,.ovr" \
		-itd \
		remotepixelapi:latest /bin/bash
	docker exec -it remotepixelapi bash -c 'unzip -q /tmp/package.zip -d /var/task/'
	docker exec -it remotepixelapi bash -c 'pip3 install boto3 jmespath python-dateutil -t /var/task'
	docker exec -it remotepixelapi python3 -c 'from remotepixel_api.landsat import search; print(search({"path": 23, "row": 31}, None))'
	docker stop remotepixelapi
	docker rm remotepixelapi

clean:
	docker stop remotepixelapi
	docker rm remotepixelapi

deploy:
	sls deploy --stage production --service cbers
	sls deploy --stage production --service landsat
	sls deploy --stage production --service sentinel
