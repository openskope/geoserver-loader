# geoserver-loader
CLI utility to load spatial layers to Geoserver.

This loader uses the Geoserver's REST API to load files into a remote
Geoserver service. The script attempts to address a couple of issues
found with pervious uses of Geoserver in a similar context. 

* Files are assumed to be "external" which means they are on the local
file system for Geoserver service. 
* Files may be local to the script host or known based on metadata
information about the file system on the  on the remote geoserver.
* Geoserver doesn't have much of a sense of hierachy but models tends tow
produce the similarly named output files. This program attempts to provide
a simple mechanism to convert filenames into a unique layer name.

```
usage: load_geoserver.py [-h] [-d] 
                        [--url URL] 
                        [-l LOGIN] [-p PASSWORD] 
                        [-workspace WORKSPACE]
                        [--style STYLE]
                        [--extpath EXTPATH]
                        [--prefix PREFIX]
                        fnames [fnames ...]

positional arguments:
  fnames                local geotiff to be added to remote geoserver

optional arguments:
  --help            show this help message and exit
  --debug           provide verbose processing  
  --url URL             geoserver rest url (default=$GEOSERVER_URL)
  --login LOGIN         geoserver login (default=$GEOSERVER_LOGIN)
  --password PASSWORD   geoserver password (default=$GEOSERVER_PASSWORD)
  --workspace WORKSPACE default workspace (default=$GEOSERVER_WORKSPACE |
                        SKOPE)
  --style STYLE         style to be applied (default=$GEOSERVER_STYLE)
  --layername TEMPLATE  layer name template (default=basename of file)
  --extpath EXTPATH     external path on geoserver prepended to all relative file paths.
  --prefix PREFIX     
```

### Examples

The following examples assume that environmental variables are set.

```shell
export GEOSERVER_URL=https://staging.openskope.org/geoserver/rest
export GEOSERVER_LOGIN=admin
export GEOSERVER_PASSWORD=xxxx
export GEOSERVER_WORKSPACE=SKOPE
```

Load the SRTM dataset with layer name 'srtm_conus'.

```shell
load_geoserver.py /projects/skope/datasets/srtm/geoserver/srtm_conus.tif
```

Load the SRTM dataset with layer name 'srtm'.

```shell
load_geoserver.py --layername srtm /projects/skope/datasets/srtm/geoserver/srtm_conus.tif
```

Load the Paleocar timeseries with multiple datasets. The following 3 examples are
equivalent. This assumes the TIFF files are local to the host where the script is 
running because of the use of the wildcard character. The layer name will be the
TIFF filename without the extensions.

```shell
load_geoserver.py /projects/skope/datasets/paleocar/geoserver/*tif
cd /projects/skope/datsets/paleocar/geoserver
load_geoserver.py --extpath /projects/skope/datasets/paleocar/geoserver *tif
cd /projects/skope/datasets
load_geoserver.py --extpath /projects/skope/datasets paleocar/geoserver/*tif
```

Load the Paleocar timeseries with multiple datasets and add paleocar version
prepended to the TIFF filename as the layer name. Note the use of curly braces
in the layername which is replaced by the TIFF file basename.

```shell
load_geoserver.py --layername 'paleocar_v2_{}' --extpath /projects/skope/datasets paleocar_v2/geoserver/*tif
```

Load the Paleocar timeseries where the script host and the geoserver host don't share
the same file system but the data files are local to the script host.

```shell
load_geoserver.py --layername 'paleocar_v2_{}' --extpath /projects/skope/datasets/paleocar/geoserver 
    --prefix /local/path/modelrun /local/path/modelrun/*tif
```

