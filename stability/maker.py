#!/usr/bin/env python

import argparse
from pathlib import Path
from glob import glob

from submitter.pysubmit import pysubmit


if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Calculate daily counts from IceTop fits files')
    p.add_argument('-t', '--tier', dest='tier',
            type=int, nargs='+',
            default=[1,2,3,4],
            help='Energy tier to run over')
    p.add_argument('-y', '--year', dest='year',
            type=int, nargs='+',
            default=list(range(2011,2023)),
            help='Calendar year to process')
    p.add_argument('--test', dest='test',
            default=False, action='store_true',
            help='Option for running off cluster to test')
    p.add_argument('--overwrite', dest='overwrite',
            default=False, action='store_true',
            help='Overwrite existing counts files')
    args = p.parse_args()

    # Get the absolute path to current directory
    script_path = Path(__file__).resolve()
    script_dir = script_path.parent
    cmd = f'{script_dir}/count_finder.py'

    # Data locations (temporary)
    prefix =
'/data/ana/CosmicRay/Anisotropy/IceTop/ITpass2/output/sidereal_unblinded/tier'
    outdir = '/data/user/cjoiner/icetop_12yr/stability'

    for year in args.year:
        for tier in args.tier:
            # Check for existing outfile
            outfile = f'{outdir}/counts_{year}_Tier{tier}.json'
            if Path(outfile).exists() and not args.overwrite:
                print(f'  Output file {outfile} already exists. Skipping...')
                continue

            # Base name for all files
            file_base = f'{prefix}{tier}/fitsbydate/{year}'

            # Some years don't have Tiers 1 and 2 (2016+)
            files = sorted(glob(f'{file_base}*/*.fits.gz'))
            if len(files) == 0:
                continue

            jobID = f'it_counts_{year}_Tier{tier}'
            ex = f'{cmd} -f {file_base} -o {outfile}'

            # Pass along environment (uses f-strings, needs python 3)
            sublines = ['getenv = True']

            # Submit
            pysubmit(ex, test=args.test, jobID=jobID, sublines=sublines)
