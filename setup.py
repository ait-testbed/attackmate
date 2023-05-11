from setuptools import setup, find_packages
from penpal.metadata import __version__

setup(
    name='penpal',
    version=__version__,
    entry_points={
        'console_scripts': [
            'penpal = penpal.__main__:main'
        ]
    },
    packages=find_packages(include=['penpal', 'penpal.*'])
)
