
from setuptools import setup, find_packages

with open('remotepixel_api/__init__.py') as f:
    for line in f:
        if line.find("__version__") >= 0:
            version = line.split("=")[1].strip()
            version = version.strip('"')
            version = version.strip("'")
            continue

# Runtime requirements.
inst_reqs = [
    "remotepixel~=2.0",
    "aws-sat-api~=2.0",
    "requests",
]

extra_reqs = {
    'test': ['mock', 'pytest', 'pytest-cov']}


setup(name='remotepixel_api',
      version=version,
      description=u"""""",
      long_description=u"",
      python_requires='>=3',
      classifiers=[
          'Programming Language :: Python :: 3.6'
      ],
      keywords='',
      author=u"Vincent Sarago",
      author_email='contact@remotepixel.ca',
      url='https://github.com/remotepixel/remotepixel-api',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=inst_reqs,
      extras_require=extra_reqs)
