
SHELL = /bin/bash

build:
	docker build --tag lambda:latest .
	docker run --name lambda -itd lambda:latest
	docker cp lambda:/tmp/package.zip package.zip
	docker stop lambda
	docker rm lambda

clean:
	docker stop lambda
	docker rm lambda

deploy:
	sls deploy --sat cbers
	sls deploy --sat landsat
	sls deploy --sat sentinel
