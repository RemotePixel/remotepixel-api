FROM amazonlinux:latest

# Configure SHELL
RUN rm /bin/sh && ln -s /bin/bash /bin/sh
ENV SHELL /bin/bash

# Install apt dependencies
RUN yum install -y gcc \
                   gcc-c++ \
                   freetype-devel \
                   yum-utils \
                   findutils \
                   openssl-devel

RUN yum -y groupinstall development

RUN curl https://www.python.org/ftp/python/3.6.1/Python-3.6.1.tar.xz | tar -xJ \
    && cd Python-3.6.1 \
    && ./configure --prefix=/usr/local --enable-shared \
    && make \
    && make install \
    && cd .. \
    && rm -rf Python-3.6.1

ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

RUN yum install -y \
   libjpeg-devel \
   zlib-devel \
   libpng-devel \
   freetype-devel \
   libcurl-devel \
   sqlite-devel.x86_64 \
   wget \
   zip \
   unzip \
   tar \
   gzip \
   libtool \
   cmake

ENV APP_DIR /tmp/app
RUN mkdir $APP_DIR

ENV PROJ_VERSION 4.9.3
RUN cd $APP_DIR \
  && wget -q https://github.com/OSGeo/proj.4/archive/$PROJ_VERSION.zip \
  && unzip $PROJ_VERSION.zip \
  && cd proj.4-$PROJ_VERSION \
  && sh autogen.sh \
  && ./configure --prefix=$APP_DIR/local \
  && make && make install && make clean \
  && rm -rf $APP_DIR/$PROJ_VERSION.zip $APP_DIR/proj.4-$PROJ_VERSION

ENV OPENJPEG_VERSION 2.1.2
RUN cd $APP_DIR \
  && wget https://github.com/uclouvain/openjpeg/archive/v$OPENJPEG_VERSION.tar.gz \
  && tar -zvxf v$OPENJPEG_VERSION.tar.gz \
  && cd openjpeg-$OPENJPEG_VERSION/ \
  && mkdir build \
  && cd build \
  && cmake -DCMAKE_INSTALL_PREFIX=$APP_DIR/local .. \
  && make install && make clean \
  && rm -rf $APP_DIR/openjpeg-$OPENJPEG_VERSION $APP_DIR/$OPENJPEG_VERSION.tar.gz

ENV GEOS_VERSION 3.5.0
RUN cd $APP_DIR \
  && wget https://github.com/libgeos/libgeos/archive/$GEOS_VERSION.tar.gz \
  && tar -zvxf $GEOS_VERSION.tar.gz \
  && cd geos-$GEOS_VERSION \
  && mkdir build \
  && cd build \
  && cmake -DCMAKE_INSTALL_PREFIX=$APP_DIR/local .. \
  && make install && make clean \
  && rm -rf $APP_DIR/libgeos-$GEOS_VERSION $APP_DIR/$GEOS_VERSION.tar.gz

ENV LD_LIBRARY_PATH=$APP_DIR/local/lib:$LD_LIBRARY_PATH

# Build and install GDAL (minimal support geotiff and jp2 support, https://trac.osgeo.org/gdal/wiki/BuildingOnUnixWithMinimizedDrivers#no1)
ENV GDAL_VERSION 2.2.0
RUN cd $APP_DIR \
  && wget http://download.osgeo.org/gdal/$GDAL_VERSION/gdal${GDAL_VERSION//.}.zip \
  && unzip gdal${GDAL_VERSION//.}.zip \
  && cd $APP_DIR/gdal-$GDAL_VERSION \
  && ./configure \
      --prefix=$APP_DIR/local \
      --with-static-proj4=$APP_DIR/local \
      --with-geos=$APP_DIR/local/bin/geos-config \
      --with-openjpeg=$APP_DIR/local \
      --with-hide-internal-symbols \
      --with-curl \
      --without-bsb \
      --without-cfitsio \
      --without-cryptopp \
      --without-ecw \
      --without-expat \
      --without-fme \
      --without-freexl \
      --without-gif \
      --without-gif \
      --without-gnm \
      --without-grass \
      --without-grib \
      --without-hdf4 \
      --without-hdf5 \
      --without-idb \
      --without-ingres \
      --without-jasper \
      --without-jp2mrsid \
      --without-jpeg \
      --without-kakadu \
      --without-libgrass \
      --without-libkml \
      --without-libtool \
      --without-mrf \
      --without-mrsid \
      --without-mysql \
      --without-netcdf \
      --without-odbc \
      --without-ogdi \
      --without-pcidsk \
      --without-pcraster \
      --without-pcre \
      --without-perl \
      --without-pg \
      --without-php \
      --without-png \
      --without-python \
      --without-qhull \
      --without-sde \
      --without-sqlite3 \
      --without-webp \
      --without-xerces \
      --without-xml2 \
    && make && make install \
    && rm -rf $APP_DIR/gdal$m{GDAL_VERSION//.}.zip $APP_DIR/gdal-$GDAL_VERSION

ENV GDAL_DATA $APP_DIR/local/lib/gdal
ENV GDAL_CONFIG $APP_DIR/local/bin/gdal-config

RUN pip3 install wheel numpy --no-binary numpy #numpy header are needed to build rasterio from source

COPY remotepixel remotepixel
RUN pip3 wheel -w /tmp/wheelhouse -e remotepixel
RUN pip3 install /tmp/wheelhouse/remotepixel-1.0.0-py3-none-any.whl --no-binary numpy,rasterio -t /tmp/vendored

COPY handler.py /tmp/vendored/handler.py

#Reduce Lambda package size (<250Mb)
RUN echo "package original size $(du -sh /tmp/vendored | cut -f1)"
RUN find /tmp/vendored \
    \( -type d -a -name test -o -name tests \) \
    -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
    -print0 | xargs -0 rm -f
RUN echo "package new size $(du -sh /tmp/vendored | cut -f1)"

RUN cd /tmp \
    && zip -r9q /tmp/package.zip vendored/*

RUN cd $APP_DIR/local \
    && zip --symlinks -r9q /tmp/package.zip lib/*.so* \
    && zip -r9q /tmp/package.zip share

RUN rm -rf /tmp/vendored/
