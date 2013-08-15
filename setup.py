from setuptools import setup

# From http://bugs.python.org/issue15881
try:
    import multiprocessing
except ImportError:
    pass

setup(
    name='mqtt-watchdir',
    url="https://github.com/jpmens/mqtt-watchdir",
    long_description=__doc__,
    install_requires=[
        'watchdog',
        'mosquitto',
    ]
)
