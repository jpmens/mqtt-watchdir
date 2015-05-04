from setuptools import setup

# from https://gist.github.com/dcreager/300803 with "-dirty" support added
from version import get_git_version

# From http://bugs.python.org/issue15881
try:
    import multiprocessing
except ImportError:
    pass

long_description = ''

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='mqtt-watchdir',
    version=get_git_version(),
    author='Jan-Piet Mens',
    author_email='jpmens@gmail.com',
    url="https://github.com/jpmens/mqtt-watchdir",
    description='Recursively watch a directory for modifications and publish file content to an MQTT broker',
    license='BSD License',
    long_description=long_description,
    keywords = [
        "MQTT",
        "files",
        "notify"
    ],
    scripts=[
        "mqtt-watchdir.py"
    ],
    data_files=[
        "README.rst"
    ],
    install_requires=[
        'watchdog',
        'paho-mqtt',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Communications',
        'Topic :: Internet',
        ]

)
