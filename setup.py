from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()

version = '0.1.0'

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://pythonhosted.org/setuptools/setuptools.html#declaring-dependencies
    box.py >= 1.2.5,
    peewee >= 2.1.7,
    pyinotify >= 0.9.4,
    tornado >= 3.2

]


setup(name='box-linux-sync',
    version=version,
    description="Linux sync client for Box.com",
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
    keywords='boxsync sync noiselabs',
    author='V\xc3\xadtor Brand\xc3\xa3o',
    author_email='vitor@noiselabs.org',
    url='https://github.com/noiselabs/box-linux-sync',
    license='LGPL-3',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ['noiselabs'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['boxsync=noiselabs.boxsync:syncd:boxsync_main',
             'boxsyncd=noiselabs.boxsync:syncd:syncd_main',
             'boxsync-webdav=noiselabs.boxsync:webdav:boxsync_main']
    }
)
