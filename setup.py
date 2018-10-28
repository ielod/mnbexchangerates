from distutils.core import setup
from setuptools import find_packages


setup(
    name='mnbexchangerates',
    version=0.1,
    install_requires=['requests'],
    entry_points={
        'console_scripts': [
            'mnb-exc-rate = mnbexchangerates.mnbexchangerates_cli:main',
        ]
    },
    url='',
    author='Elod Illes',
    description='Fetch MNB exchange rates',
    packages=find_packages(),
)
