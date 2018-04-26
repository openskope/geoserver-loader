#!/usr/bin/env python2
"""
Modeled after gdallocationinfo, this tool is designed to efficiently
generate zonal statistics for a single region. Inputs include a raster 
file such as a GeoTiff and a geojson-like file or string. Only Point
and Polygon GeoJSON types are currently supported.

The stats generated can include mean, min, max, and std. A pseudo-method
called 'standard' will generate all 4 statistics.

If the raster contains multiple bands the tools will loop through each band
and determine the numerical value for every pixel within the boundary of
the GeoJSON.
"""

import sys
import argparse
import json
import numpy as np
import rasterio
from rasterio.mask import mask, raster_geometry_mask
import time

import logging
log = logging.getLogger('zonalinfo')


GEOM_TYPES = { 'Point', 'Polygon' }


def read_geometry(fname):

    if fname == '-':
        boundary = json.load(sys.stdin)

    else: 
        with open(fname) as f:
            boundary = json.load(f)

    if 'geometry' in boundary.keys():
        return boundary['geometry']

    if boundary.get('type', '') in GEOM_TYPES:
        return boundary

    raise RuntimeError('%s did contain geometry', fname)


def write_json(results):
    for arr in 'mean min max std'.split():
        if arr in results.keys():
            results[arr] = results[arr]

    if 'window' in results.keys():
        results['window'] = results['window']

    sys.stdout.write(json.dumps(results))


def write_values(results, method):

    for i in range(results['count']):
        if method == 'standard':
            print('%3.6f, %3.6f, %3.6f %3.6f' % (results['mean'][i],
                results['min'][i], results['max'][i]), results['std'])
        else:
            print('%3.6f' % (results[method][i]))

    return

def write_gdallocationinfo(results, method):
    """Write results in a format similar to gdallocationinfo."""

    for i in range(results['count']):
        print('  Band %d:' % (i+1))
        if method == 'standard':
            print('    Values: %3.6f, %3.6f, %3.6f, %3.6f' % (
                    results['mean'][i], results['min'][i], 
                    results['max'][i], results['std'][i]))
        else:
            print('    Value: %3.6f' % results[method][i])


def add_local_args(parser):

    parser.add_argument('raster', metavar='FILE',
        help='path to the raster dataset')
    parser.add_argument('--geometry', '-g', required=True,
        help='file with geojson-like object (use "-" for stdin)')
    parser.add_argument('--json', default=False, action='store_true',
        help='output in json format (default=False)')
    parser.add_argument('--valonly', default=False, action='store_true',
        help='only output the method value (default=False)')
    parser.add_argument('--method', default='mean', 
        help='specify the aggregation method (default=mean)')
    parser.add_argument('--debug', default=logging.WARN,
        const=logging.DEBUG, action='store_const',
        help='enable debugging information')


def main():

    parser = argparse.ArgumentParser(description=__doc__)
    add_local_args(parser)
    args = parser.parse_args()
    
    logging.basicConfig(level=args.debug)

    # currently handling a single geometry at a time
    geoms = [read_geometry(args.geometry)]

    if args.method == 'standard':
        zonal = dict(mean=[], min=[], max=[], std=[])
    else:
        zonal = { args.method: [] }

    with rasterio.open(args.raster) as src:
        masked, transform, window = raster_geometry_mask(src, geoms, crop=True, all_touched=True)
        zonal['window'] = window
        zonal['count'] = src.count
        zonal['band'] = range(src.count)

        for i in range(src.count):
            data = src.read(i+1, window=window)
            values = np.ma.array(data=data, 
                    mask=np.logical_or(np.equal(data, src.nodata), masked))

            if args.method == 'mean' or args.method == 'standard':
                zonal['mean'].append(np.mean(values))
            if args.method == 'min' or args.method == 'standard':
                zonal['min'].append(np.min(values))
            if args.method == 'max' or args.method == 'standard':
                zonal['max'].append(np.max(values))
            if args.method == 'std' or args.method == 'standard':
                zonal['std'].append(np.std(values))

    
    if args.json:
        write_json(zonal)

    elif args.valonly:
        write_values(zonal, args.method)

    else:
        write_gdallocationinfo(zonal, args.method)


if __name__ == '__main__':
    main()
