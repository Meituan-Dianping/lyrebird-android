from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='lyrebird-android',
    version='0.5.7',
    packages=['lyrebird_android'],
    url='https://github.com/meituan/lyrebird-android',
    author='HBQA',
    author_email='',
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    zip_safe=False,
    classifiers=(
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
    ),
    entry_points={
        'lyrebird_plugin': [
            'android = lyrebird_android.manifest'
        ]
    },
    install_requires=[
        'lyrebird'
    ]
)
