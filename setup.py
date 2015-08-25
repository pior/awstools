from setuptools import setup, find_packages
import codecs

version = '0.3.11.dev0'


def read(filename):
    return unicode(codecs.open(filename, encoding='utf-8').read())

long_description = '\n\n'.join([read('README.rst'), read('CHANGES.rst')])

setup(
    name='awstools',
    version=version,
    description="High level tools to manage an AWS infrastructure",
    long_description=long_description,
    classifiers=[
        "Intended Audience :: System Administrators",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='',
    author='Pior Bastida',
    author_email='pbastida@ludia.com',
    url='https://github.com/ludia/awstools',
    license='GPL',
    packages=find_packages(),
    # include_package_data=True,
    zip_safe=False,
    install_requires=[
        "argh >= 0.26",
        "PyYaml",
        "boto",
        "arrow",
        "prettytable",
    ],
    extras_require={
        'test': ['nose', 'nosexcover', 'coverage', 'mock', 'zest.releaser'],
        },
    entry_points={
        'console_scripts': [
            'cfnas = awstools.commands.cfnautoscale:main',
            'cfn = awstools.commands.cloudformation:main',
            'ec2ssh = awstools.commands.ec2ssh:main',
        ]
    }
)
