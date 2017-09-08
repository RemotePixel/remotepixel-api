FROM remotepixel/amazonlinux-gdal:latest

COPY remotepixel remotepixel
RUN pip3 wheel -w /tmp/wheelhouse -e remotepixel  --no-deps
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
