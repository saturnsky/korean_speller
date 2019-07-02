import os
import os.path
import codecs

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def read_me():
    with codecs.open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding="utf-8") as f:
        return f.read()


def get_version():
    with codecs.open(os.path.join(os.path.dirname(__file__), 'VERSION'), encoding="utf-8") as f:
        return f.read()

setup(
    name='KoreanSpeller',
    version=get_version(),
    description=read_me(),
    author='karipe',
    author_email='ikadro@gtbook.net',
    url='https://github.com/karipe/korean_speller',
    packages=['korean_speller'],
    install_requires=[
        'requests',
    ]
)
