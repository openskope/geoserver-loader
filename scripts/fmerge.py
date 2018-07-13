import os
import sys
from argparse import ArgumentParser
import logging
from progress.bar import Bar
import rasterio


def add_local_arguments(parser):
    parser.add_argument('--profile', metavar='FILE', 
            help='file to be used as profile for output file '
                 '(default=first input file)')
    parser.add_argument('--debug', '-d', default=logging.WARN, 
        const=logging.DEBUG, action='store_const',
        help='enable debugging messages (default=WARN)')
    parser.add_argument('--verbose', '-v', default=False, action='store_true',
            help='provide progress information to stdout')
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
        log.debug('no output file specified')
        parser.print_help(sys.stderr)
        sys.exit(1)

    if len(args.inputs) < 2:
        log.debug('too few input file specified')
        parser.print_help(sys.stderr)
        sys.exit(2)

    # get the profile
    if not args.profile:
        args.profile = args.inputs[0]
        log.debug('output file = %s', args.profile)
    with rasterio.open(args.profile) as src:
        profile = src.profile
        profile.update(count=len(args.inputs))
    log.debug(profile)

    # copy each input as a band
    bar = Bar('Processing', max=len(args.inputs))
    with rasterio.open(args.output, 'w', **profile) as dst:
        for idx,fname in enumerate(args.inputs):
            bar.next()
            with rasterio.open(fname) as src:
                data = src.read(1)
                log.debug(data)
                dst.write_band(idx+1, data)
    bar.finish()
    

if __name__ == '__main__':
    main()
