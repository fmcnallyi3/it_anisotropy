#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py3-v4.4.2/icetray-start
#METAPROJECT: icetray/v1.17.0

import uproot
import json
import numpy as np
import argparse

def dt_extractor(root_files, out_file):

    # Default binning
    bins = np.linspace(-10, 3, 201)

    # Storage
    h_tot = np.zeros(len(bins) - 1)
    start_times = []
    stop_times  = []

    for root_file in root_files:

        print(f'Working on {root_file}...')

        with uproot.open(root_file) as f:
            event_header = f['I3EventHeader']
            mjd = event_header['time_start_mjd'].array(library='np')
            run = event_header['Run'].array(library='np')

        # Objective: handle in-run δt's and between-run δt's separately
        unique_runs = sorted(set(run))
    
        for run_no in unique_runs:

            # Only select times corresponding to a given run (and sort)
            run_cut = (run == run_no)
            run_mjd = np.sort(mjd[run_cut])

            # Calculate in-run δt's and store in histogram
            dt = run_mjd[1:] - run_mjd[:-1]
            dt[dt==0] = 10**(bins.min())  # 0's eliminated for future log-view
            h,_ = np.histogram(np.log10(dt), bins=bins)
            h_tot += h

            # Store start and stop for between-run δt calculation later
            start_times += [run_mjd.min()]
            stop_times  += [run_mjd.max()]

    # Write and save
    data = {'hist':h.tolist(),
            'bins':bins.tolist(), 
            'start':start_times,
            'stop':stop_times}

    with open(out_file, 'w') as f:
        json.dump(data, f, indent=4)



if __name__ == "__main__":

    p = argparse.ArgumentParser()
    p.add_argument('-f', '--files', dest='files',
            nargs='+',
            help='Root files to process')
    p.add_argument('-o', '--out', dest='out',
            help='Output file name for saved histogram')

    args = p.parse_args()

    dt_extractor(args.files, args.out)
