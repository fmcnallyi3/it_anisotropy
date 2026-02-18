#!/usr/bin/env python

import numpy as np
import json
import getpass
from pathlib import Path


def hist_merger(hist_files, out_file):

    # Storage for run start/stop times
    start_times = []
    stop_times  = []
    
    for i, hist_file in enumerate(hist_files):

        # Load data from each histogram file
        with open(hist_file, 'r') as f:
            data_i = json.load(f)

        # Store the start and stop times
        start_times += data_i['start']
        stop_times  += data_i['stop']

        # Initialize dictionary with first entry
        if i == 0:
            data = data_i
            data['hist'] = np.array(data['hist'])
            continue

        # Add to running total
        data['hist'] += np.array(data_i['hist'])

    # Make sure to include the δt that happens between files
    start_times = np.sort(start_times)
    stop_times  = np.sort(stop_times)

    dt = start_times[1:] - stop_times[:-1]
    dt[dt==0] = np.min(data['bins'])
    interfile_h,_ = np.histogram(np.log10(dt), bins=data['bins'])
    data['run_hist'] = interfile_h

    # Revert numpy array to list
    data['hist'] = data['hist'].tolist()
    data['run_hist'] = data['run_hist'].tolist()

    with open(out_file, 'w') as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":

    user = getpass.getuser()

    out_dir = Path(f'/data/user/{user}/stability/icetop_dt')
    hist_files = sorted(out_dir.glob('hist_???.json'))
    out_file = out_dir / 'hist_combined.json'

    hist_merger(hist_files, out_file)

