
import os

from setuptools import setup, find_packages

with open('remotepixel/__init__.py') as f:
    for line in f:
        if line.find("__version__") >= 0:
            version = line.split("=")[1].strip()
            version = version.strip('"')
            version = version.strip("'")
            break


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='remotepixel',
    version=version,
    description=u"",
    long_description=u"",
    classifiers=[
        'Programming Language :: Python :: 3.6'
    ],
    keywords='remotepixel AWS lambda Landsat Sentinel SRTM',
    author=u"Vincent Sarago",
    author_email='contact@remotepixel.ca',
    url='https://github.com/remotepixel/remotepixel-api',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    python_requires='~=3.6',
    package_data={'remotepixel': ['cmap.txt']},
    install_requires=read('requirements.txt').splitlines(),
    extras_require={
        'test': ['pytest', 'pytest-cov', 'codecov'],
    })
