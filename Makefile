
SHELL = /bin/bash

build:
	docker build --tag lambda:latest .
	docker run --name lambda -itd lambda:latest /bin/bash
	docker cp lambda:/tmp/package.zip package.zip
	docker stop lambda
	docker rm lambda

clean:
	docker stop lambda
	docker rm lambda

deploy:
	sls deploy --stage production --service cbers
	sls deploy --stage production --service landsat
	sls deploy --stage production --service sentinel
