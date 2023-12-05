import os.path
from setuptools import setup

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

# This call to setup() does all the work
setup(
    name="dadi-cli",
    version="0.9.4b",
    description="A command line interface for dadi",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/xin-huang/dadi-cli",
    author="Xin Huang; Travis J. Struck; Sean W. Davey; Ryan N. Gutenkunst",
    author_email="xinhuang.res@gmail.com; rgutenk@arizona.edu",
    license="Apache-2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    packages=["dadi_cli"],
    include_package_data=True,
    # install_requires=[
    #    "dadi"
    # ],
    entry_points={"console_scripts": ["dadi-cli=dadi_cli.__main__:main"]},
)
