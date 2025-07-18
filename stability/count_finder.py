#!/usr/bin/env python

import argparse
import json
import re
import numpy as np
import healpy as hp

from glob import glob
from collections import defaultdict


def get_counts(filelist, outfile):

    # Create dict with format: counts[date] = nevents
    counts = defaultdict(int)

    # Parse filelist for dates
    dates = [re.findall('\d{4}-\d{2}-\d{2}', f)[-1] for f in filelist]
    dates = sorted(set(dates))

    # Sum the counts for each day and store in dictionary
    for day in dates:
        day_files = [f for f in filelist if day in f]
        for map_file in day_files:
            print(f'Reading {map_file}...')
            data = hp.read_map(map_file, verbose=False)
            counts[day] += int(data.sum())

    # Write to a file
    with open(outfile, 'w') as f:
        json.dump(counts, f)



if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Calculate daily counts from IceTop fits files')
    p.add_argument('-f', '--file_base', dest='file_base',
            type=str,
            help='Base string for input files to run over')
    p.add_argument('-o', '--outfile', dest='outfile',
            type=str,
            help='Output file name')
    args = p.parse_args()

    # File collection here because there are too many files for argparse
    files = sorted(glob(f'{args.file_base}*/*.fits.gz'))

    # Execute
    get_counts(files, args.outfile)



