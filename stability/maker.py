#!/usr/bin/env python

import argparse
from pathlib import Path

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
    args = p.parse_args()

    # Get the absolute path to current directory
    script_path = Path(__file__).resolve()
    script_dir = script_path.parent

    cmd = f'{script_dir}/count_finder.py'

    for year in args.year:
        for tier in args.tier:

            # Establish executable and jobID
            jobID = f'it_counts_{year}_Tier{tier}'
            ex = f'{cmd} -t {tier} -y {year}'
            if args.test:
                ex = f'{ex} --test'

            # Pass along environment (uses f-strings, needs python 3)
            sublines = ['getenv = True']

            # Submit
            print(ex)
            pysubmit(ex, test=args.test, jobID=jobID, sublines=sublines)

