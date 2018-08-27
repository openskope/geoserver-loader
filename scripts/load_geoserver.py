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

    parser.add_argument('--layername', default='{}',
        help='layer name (defaults to filename without path or ext)')
    parser.add_argument('-e', '--extpath', default='',
        help='external path prepended to all filename arguments')
    parser.add_argument('--prefix', default='',
        help='prefix to be removed from all filename arguments')
    parser.add_argument('fnames', nargs='+',
        help='external geotiff filename to be added to remote geoserver')
    parser.add_argument('-d', '--debug', default=logging.WARNING,
        const=logging.DEBUG, action='store_const',
        help='provide verbose processing')


def get_catalog(args):

    if not args.url:
        raise RuntimeError, 'geoserver url must be provided'

    if not args.password:
        raise RuntimeError, 'geoserver password must be provided.'

    return Catalog(args.url, args.login, args.password)


def get_layer_name(fname, template='{}'):
    """create layer name based on filename

    Get the base filename from the fname argument by removing any path
    or extensions. Create layer name by formating the template string
    with one argument, the base filename.

    Args:
      fname (str): absolule or relative filename
      template (str): layer name template

    Returns:
      (str): layer name
    """

    head, tail = os.path.split(fname)
    if tail == '':
        raise RuntimeError, 'bad filename argument, must not end with a /'
    base, ext = os.path.splitext(tail)

    layername = template.format(base)
    logging.debug('layer name = %s', layername)
    return layername


def get_external_path(extpath, fname, prefix = ''):
    """remove fname prefix and prepend external path"""

    if prefix and fname.startswith(prefix):
        fname = fname[len(prefix):]
        if fname[0] == '/':
            fname = fname[1:]

    uri = 'file://' + os.path.join(extpath, fname)
    logging.debug('external path = %s', uri)
    return uri


def set_default_style(cat, layername, stylename):
    """find layer and apply a style if one is given"""
    
    if stylename:
        style = cat.get_style(stylename)
    else:
        logging.warn('no style provided, layer will use geoserver defaults')

    if not style:
        logging.error('style not found, layer will use geoserver defaults')
        return

    logging.debug('applying style %s to layer %s', stylename, layername)
    layer = cat.get_layer(layername)
    if not layer:
        logging.error('layer %s not found, no style applied', layername)
        return

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
    
    for fname in args.fnames:
        logging.debug('fname argument = %s', fname)
        layername = get_layer_name(fname, template=args.layername)
        extpath = get_external_path(args.extpath, fname, prefix=args.prefix)
        cat.create_coveragestore_external_geotiff(layername, extpath)
        set_default_style(cat, layername, args.style)


if __name__ == '__main__':
    main()    
