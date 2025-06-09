#!/usr/bin/env python

import argparse
import json
import numpy as np
import healpy as hp

from glob import glob
from collections import defaultdict


def get_counts(year, tier, test=False):

    prefix = '/data/ana/CosmicRay/Anisotropy/IceTop/ITpass2/output/outputa'

    # Create dict with format: counts[date][tier] = nevents
    counts = defaultdict(lambda: defaultdict(int))

    # Last directory is sometimes ITpass2 and sometimes ITpass2_sd?
    tier_path = f'{prefix}/tier{tier}_unblinded/ITpass2*'
    days = sorted(glob(f'{tier_path}/{year}-*'))
    if test:
        days = days[:3]

    for day in days:

        # Get date out of file path
        yyyymmdd = day.split('/')[-1]

        # Sum the counts from all corresponding map files
        map_files = sorted(glob(f'{day}/*.fits.gz'))
        if test:
            map_files = map_files[:3]

        for map_file in map_files:
            print(f'Reading {map_file}...')
            data = hp.read_map(map_file, verbose=False)
            counts[yyyymmdd][tier] += int(data.sum())

    # Don't write empty dictionaries
    if len(counts.keys()) == 0:
        return

    # Write to a file
    out_dir = '/data/user/fmcnally/icetop_12yr/stability'
    with open(f'{out_dir}/counts_{year}_Tier{tier}.json', 'w') as f:
        json.dump(counts, f)



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
    args = p.parse_args()

    for year in args.year:
        for tier in args.tier:
            get_counts(year, tier, test=args.test)



