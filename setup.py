import pygwidget
from setuptools import setup, find_packages


setup(
    name='pygwidget',
    version=pygwidget.__version__,
    packages=find_packages(),
    py_modules=['pygwidget'],
    license='MIT',
)
