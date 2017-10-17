from distutils.core import setup

setup(
    name='juramote',
    version='0.1.0',
    author='Lars-Dominik Braun',
    author_email='lars+juramote@6xq.net',
    packages=['juramote'],
    url='https://6xq.net/juramote/',
    license='LICENSE.txt',
    description='Remote control for Jura coffee maker.',
    long_description=open('README.rst').read(),
    install_requires=[
        'pyserial>=3',
        'Flask',
        'wtforms',
    ],
    entry_points={
    'console_scripts': [
            'juramotecli = juramote.cli:main',
            'juramotehttpd = juramote.server:main'],
    },
)
