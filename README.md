# geoserver-loader
CLI utility to load spatial layers to Geoserver.

This loader uses the Geoserver's REST API to load files into a remote
Geoserver service. The script attempts to address a couple of issues
found with pervious uses of Geoserver in a similar context. 

* Files are assumed to be "external" which means they are on the local
file system for both Geoserver service and the script. The path doesn't
need to be the same (but everybody's life is easier if it is).
* Geoserver doesn't have much of a sense of hierachy but models tends to
produce the similarly named output files. This program attempts to provide
a simple mechanism to convert file path and filename components into a
unique layer name.

