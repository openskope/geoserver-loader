import os
import sys
from argparse import ArgumentParser
import logging
import rasterio


def add_local_arguments(parser):
    parser.add_argument('--profile', '-p', metavar='FILE', 
            help='file to be used as profile for output file '
                 '(default=first input file)')
    parser.add_argument('--debug', '-d', default=logging.WARN, 
        const=logging.DEBUG, action='store_const',
        help='enable debugging messages (default=WARN)')
    parser.add_argument('--output', '-o', required=True,
            help='output filename (required)')
    parser.add_argument('inputs', nargs='+', help='two or more input files')


def main():
    parser = ArgumentParser()
    add_local_arguments(parser)
    args = parser.parse_args()

    logging.basicConfig(level=args.debug)
    log = logging.getLogger(os.path.basename(sys.argv[0]))

    if not args.output:
        parser.print_help(sys.stderr)
        sys.exit(1)

    if len(args.inputs) < 2:
        parser.print_help(sys.stderr)
        sys.exit(2)

    # get the profile
    if not args.profile:
        args.profile = args.inputs[0]
    with rasterio.open(args.profile) as src:
        profile = src.profile
    log.debug(profile)

    # copy each input as a band
    with rasterio.open(args.output, 'w', **profile) as dst:
        for idx,fname in enumerate(args.inputs):
            with rasterio.open(fname) as src:
                dst.write_band(idx+1, src.read())
    

if __name__ == '__main__':
    main()
