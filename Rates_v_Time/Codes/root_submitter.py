#!/usr/bin/env python

from submitter.pysubmit import pysubmit
import argparse
from glob import glob
import re
import os
import directories as stab


if __name__ == "__main__":

    stab.setup_dirs()   

    p = argparse.ArgumentParser(
            description='Cluster submission for root_extractor.py')
    p.add_argument('--test', dest='test',
            default=False, action='store_true',
            help='Option for running off cluster to test')
    p.add_argument('-c', '--config', dest='config',
            help='Detector season [IC86-2011 - IC86-2022]')
    p.add_argument('-d', '--dates', dest='dates',
            nargs='*',
            help='List of dates to run over')
    p.add_argument('-o', '--outDir', dest='outDir',
            default=stab.root_out,
            help='Output directory')
    p.add_argument('--overwrite', dest='overwrite',
            default=False, action='store_true',
            help='Overwrite existing output summary files')
    args = p.parse_args()


    # Output location for submitter files
    npx_out = f'{stab.home}/submitter'

    # Collect all files from specified detector configuration
    prefix = '/data/ana/CosmicRay/Anisotropy/IceCube'
    files = glob(f'{prefix}/{args.config}/**/*.root', recursive=True)
    files.sort()

    # Group all files according to a given date
    dates = args.dates
    if dates == None:
        dates = set([re.findall('\d{4}-\d{2}-\d{2}', f)[-1] for f in files])
    dates = sorted(dates)
    if args.test:
        dates = dates[:2]

    # Environment for script
    cvmfs = '/cvmfs/icecube.opensciencegrid.org/py3-v4.1.1/icetray-start'
    meta = 'icetray/stable'
    header = [f'#!/bin/sh {cvmfs}', f'#METAPROJECT {meta}']
    # ROOT tools not automatically loaded
    header += ['export PYTHONPATH="$PYTHONPATH:${SROOT}/lib"']
    # Request increased memory: 8 GB (shouldn't need more than 4)
    sublines = ["request_memory = 2000"]  

    # Run over all dates
    for date in dates:

        # Limit to relevant files
        files_i = sorted([f for f in files if date in f])
        if files_i == []:
            print(f'No files found for {date}! Skipping...')
            continue

        # Run
        files_i = ' '.join(files_i)
        out = f'{args.outDir}/sum_{args.config}_{date}.txt'
        cmd = f'{stab.home}/root_extractor.py -i {files_i} -o {out}'

        if os.path.isfile(out) and not args.overwrite:
            #print(f'Files {out} already exists! Skipping...')
            continue

        pysubmit(cmd, npx_out, test=args.test, header=header, sublines=sublines)
