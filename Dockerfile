FROM amazonlinux:latest

# Install apt dependencies
RUN yum install -y gcc gcc-c++ freetype-devel yum-utils findutils openssl-devel

RUN yum -y groupinstall development

RUN curl https://www.python.org/ftp/python/3.6.1/Python-3.6.1.tar.xz | tar -xJ \
    && cd Python-3.6.1 \
    && ./configure --prefix=/usr/local --enable-shared \
    && make \
    && make install \
    && cd .. \
    && rm -rf Python-3.6.1

ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

RUN pip3 install numpy --no-binary numpy

# Install Python dependencies
# RUN pip3 install remotepixel==1.0.0 aws-sat-api==0.0.4 --no-binary numpy -t /tmp/vendored -U
RUN pip3 install git+https://github.com/RemotePixel/remotepixel-py.git@29f2c3c070679b4371379de9c40c2fb72cf3803c aws-sat-api==0.0.4 --no-binary numpy -t /tmp/vendored -U

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

COPY app /tmp/vendored/app

# Create archive
RUN cd /tmp/vendored && zip -r9q /tmp/package.zip *

# Cleanup
RUN rm -rf /tmp/vendored/
