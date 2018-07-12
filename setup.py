from setuptools import setup, find_packages

def readme():
    try:
        with open('README.md') as f:
            return f.read()
    except IOError as e:
        return ''


setup(
    name="skope_utils",
    version="1.0.0",
    author="Jeff Terstriep",
    author_email="jefft@illinois.edu",
    description="Collection of scripts for interacting with SKOPE",
    long_description=readme(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        'gsconfig',
        'rasterio>=1.0a12',
        'rasterstats',
        'fiona',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],

    scripts=[
        'scripts/zonalinfo.py',
        'scripts/load_paleocar.py',
        'scripts/fmerge.py',
        'scripts/convert.sh'
    ]

)
