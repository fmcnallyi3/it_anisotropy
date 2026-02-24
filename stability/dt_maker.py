#!/usr/bin/env python

from pathlib import Path
import numpy as np
import subprocess
import getpass
import argparse

from submitter.pysubmit import pysubmit
from dt_extractor import dt_extractor

if __name__ == "__main__":

    p = argparse.ArgumentParser()
    p.add_argument('--overwrite', dest='overwrite',
            default=False, action='store_true',
            help='Optionally overwrite existing histogram files')
    p.add_argument('--test', dest='test',
            default=False, action='store_true',
            help='Submit a small sample to the cluster to test')
    args = p.parse_args()

    # Determine paths to root files
    root_dir = '/data/ana/CosmicRay/Anisotropy/IceTop/ITpass2'
    root_files = sorted([p for p in Path(root_dir).glob('l3_*.root')])

    # Establish path for output, creating directory if it doesn't exist
    user = getpass.getuser()
    out_dir  = Path(f'/data/user/{user}/stability/icetop_dt')
    out_dir.mkdir(parents=True, exist_ok=True)

    # Split root files into jobs for submission (<10 mins per job)
    njobs = 50
    sub_lists = np.array_split(root_files, njobs, axis=0)
    if args.test:
        sub_lists = sub_lists[:1]

    for i, root_files in enumerate(sub_lists):

        # Check to see if output file already exists
        out_file = out_dir / f'hist_{i:03d}.json'
        if out_file.exists() and not args.overwrite and not args.test:
            continue

        # Change output name and shorten file list if running as test
        if args.test:
            out_file = out_dir / 'hist_test.json'
            root_files = root_files[:3]

        # Command to run
        cwd = Path(__file__).parent.resolve()
        cmd = f'{cwd}/dt_extractor.py'

        # Input root files as a string
        file_str = ' '.join([str(f) for f in root_files])

        # Combined executable with arguments
        ex = f'{cmd} -f {file_str} -o {out_file}'

        # Submit to cluster
        jobID = f'dt_{out_file.name}'
        pysubmit(ex, jobID=jobID)

