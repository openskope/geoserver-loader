"""Command line tool to load GeoTIFFs into a remote Geoserver.

This tool assumes the geoserver has local access to the same files
as the host where the command line tool is running and therefor uses
the 'external' method available to the REST methods. 
"""
import os
import sys
import logging
from argparse import ArgumentParser
from geoserver.catalog import Catalog


def add_geoserver_args(parser):
    parser.add_argument('-u', '--url',
        default=os.environ.get('GEOSERVER_URL', ''),
        help='url (default=$GEOSERVER_URL)')
    parser.add_argument('-l', '--login',
        default=os.environ.get('GEOSERVER_LOGIN', 'admin'),
        help='login (default=$GEOSERVER_LOGIN)')
    parser.add_argument('-p', '--password',
        default=os.environ.get('GEOSERVER_PASSWORD', ''),
        help='password (default=$GEOSERVER_PASSWORD)')
    parser.add_argument('-w', '--workspace',
        default=os.environ.get('GEOSERVER_WORKSPACE', 'SKOPE'),
        help='default workspace (default=$GEOSERVER_WORKSPACE | SKOPE)')
    parser.add_argument('--style',
        default=os.environ.get('GEOSERVER_STYLE', ''),
        help='style to be applied (default=$GEOSERVER_STYLE)')


def add_local_args(parser):
    parser.add_argument('-f', '--format', default='',
        help='dynamically create layer name from path (default=basename)')
    parser.add_argument('-e', '--extpath', default='',
        help='external path prepended to all relative file paths.')
    parser.add_argument('-m', '--matchpath', default='',
        help='matches local path to replaces it with external path')
    parser.add_argument('fnames', nargs='+',
        help='local geotiff to be added to remote geoserver')
    parser.add_argument('-d', '--debug', default=logging.WARN,
        const=logging.DEBUG, action='store_const',
        help='provide verbose processing')


def get_catalog(args):

    if not args.url:
        raise RuntimeError, 'geoserver url must be provided'

    if not args.password:
        raise RuntimeError, 'geoserver password must be provided.'

    return Catalog(args.url, args.login, args.password)


def get_layer_name(fname, _format='{three}'):
    """create layer name based on filename and path"""

    fbase, ext = os.path.splitext(fname)

    path = fbase.split('/')
    while path[0] == '':
        path.pop(0)

    name = _format.format(*path, one=path[-3], two=path[-2], three=path[-1])
    logging.debug('layer_name = %s', name)
    return name


def get_external_path(fname, base, prefix):
    """remove fname prefix and prepend base"""

    if prefix and fname.startswith(prefix):
        fname = fname[len(prefix):]
        if fname[0] == '/':
            fname = fname[1:]

    logging.debug('%s, %s', base, fname)
    uri = 'file://' + os.path.join(base, fname)
    logging.debug('external path = %s', uri)
    return uri


def validate_file(fname):
    """basic sanity check on the local file"""
    if not os.path.exists(fname):
        logging.warn('file missing or unreadable: %s', fname)
        return False

    return True    


def set_default_style(cat, name, style):
    """find layer and apply a style if one is given"""
    
    if style:
        layer = cat.get_layer(name)
        layer.default_style = style
        cat.save(layer)


def main():

    parser = ArgumentParser(description=__doc__)
    add_geoserver_args(parser)
    add_local_args(parser)
    args = parser.parse_args()

    logging.basicConfig(level=args.debug)

    try:
        cat = get_catalog(args)
        cat.workspace = args.workspace
        logging.debug('default workspace set to %s', args.workspace)
    except RuntimeError, e:
        logging.error('Unable to connect to Geoserver: %s', e)
        sys.exit(-1)
    
    style = None
    if args.style:
        style = cat.get_style(args.style)

    for fname in args.fnames:
        logging.debug('local path = %s', fname)
        if validate_file(fname):
            name = get_layer_name(fname, args.format)
            path = get_external_path(fname, args.extpath, 
                                     prefix=args.matchpath)
            cat.create_coveragestore_external_geotiff(name, path)
            set_default_style(cat, name, style)


if __name__ == '__main__':
    main()    
