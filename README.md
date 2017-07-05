# remotepixel-api
Process Landsat and Sentinel data using AWS Lambda functions

=========

### What this is


### How to use


### Requierement
  - AWS Account
  - awscli
  - Docker
  - npm


### Creating a python lambda package: Docker

```
make build && make package
```

### Deploy: Serverless
```
npm install -g serverless

make deploy-us && make deploy-eu
```
