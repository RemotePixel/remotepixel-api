FROM remotepixel/amazonlinux-gdal:2.4.0

WORKDIR /tmp
COPY setup.py setup.py
COPY remotepixel_api/ remotepixel_api/

# Install dependencies
RUN pip3 install . --no-binary numpy,rasterio -t /tmp/vendored -U

# Reduce Lambda package size to fit the 250Mb limit
# Mostly based on https://github.com/jamesandersen/aws-machine-learning-demo
RUN du -sh /tmp/vendored

# This is the list of available modules on AWS lambda Python 3
# ['boto3', 'botocore', 'docutils', 'jmespath', 'pip', 'python-dateutil', 's3transfer', 'setuptools', 'six']
RUN find /tmp/vendored -name "*-info" -type d -exec rm -rdf {} +
RUN rm -rdf /tmp/vendored/boto3/
RUN rm -rdf /tmp/vendored/botocore/
RUN rm -rdf /tmp/vendored/docutils/
RUN rm -rdf /tmp/vendored/dateutil/
RUN rm -rdf /tmp/vendored/jmespath/
RUN rm -rdf /tmp/vendored/s3transfer/
RUN rm -rdf /tmp/vendored/numpy/doc/

# Leave module precompiles for faster Lambda startup
RUN find /tmp/vendored -type f -name '*.pyc' | while read f; do n=$(echo $f | sed 's/__pycache__\///' | sed 's/.cpython-36//'); cp $f $n; done;
RUN find /tmp/vendored -type d -a -name '__pycache__' -print0 | xargs -0 rm -rf
RUN find /tmp/vendored -type f -a -name '*.py' -print0 | xargs -0 rm -f

RUN du -sh /tmp/vendored

RUN cd $APP_DIR/local && find lib -name \*.so\* -exec strip {} \;
RUN cd $APP_DIR/local && find lib64 -name \*.so\* -exec strip {} \;

################################################################################
#                              CREATE ARCHIVE                                  #
################################################################################

RUN cd /tmp/vendored && zip -r9q /tmp/package.zip *
RUN cd $APP_DIR/local && zip -r9q --symlinks /tmp/package.zip lib/*.so*
RUN cd $APP_DIR/local && zip -r9q --symlinks /tmp/package.zip lib64/*.so*
RUN cd $APP_DIR/local && zip -r9q /tmp/package.zip share

# Cleanup
RUN rm -rf /tmp/vendored/
