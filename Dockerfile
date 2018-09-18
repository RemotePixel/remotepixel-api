FROM lambdalinux/baseimage-amzn:2017.03-004

RUN yum update -y && yum upgrade -y
RUN yum install -y python36-devel python36-pip
RUN yum clean all

ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

# install system libraries
RUN yum makecache fast
RUN yum install -y gcc gcc-c++ freetype-devel yum-utils findutils openssl-devel wget tar unzip zip bzip2 gzip
RUN yum clean all

RUN pip-3.6 install pip -U

ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# Install Python dependencies
RUN pip3 install remotepixel==2.0.0 aws-sat-api~=2.0 requests --no-binary numpy -t /tmp/vendored -U

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
