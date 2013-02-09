from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


version = '0.1.0'

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
]


setup(name='box-linux-sync',
    version=version,
    description="Linux client for Box.com",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Communications :: File Sharing',
        'Topic :: Utilities'
    ],
    keywords='box sync noiselabs',
    author='V\xc3\xadtor Brand\xc3\xa3o',
    author_email='noisebleed@noiselabs.org',
    url='https://github.com/noisebleed/box-linux-sync',
    license='LGPL-3',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ['noiselabs'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['box-linux-sync=noiselabs.box:main']
    }
)
