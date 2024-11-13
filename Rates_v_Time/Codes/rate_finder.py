#!/usr/bin/env python

########################################################################
###    Code meant to summarize all data-checking results. Combines   ###
###    information from I3 livetime, root files, and fits files to   ###
###    output rates and store a summary of every run.                ###
########################################################################


import re
import json

from grl_reader import get_livetime, get_bad_runs
import directories as stab


if __name__ == "__main__":

    # Load default project-associated paths
    stab.setup_dirs()

    # File locations
    map_dir = '/data/user/fmcnally/anisotropy/maps'

    # Extract livetime and bad runs from good run list
    goodrunfile = f'{stab.data}/goodrunlist.json'
    run2cfg = f'{stab.data}/run2cfg.json'
    i3_livetime = get_livetime(goodrunfile, run2cfg)
    badruns = get_bad_runs(goodrunfile)

    # Load map counts for all detector configurations
    print('Loading fits data...')
    with open(f'{stab.data}/fits_summary.json', 'r') as f:
        fits_data = json.load(f)

    # Load counts and livetimes from root files
    print('Loading root data...')
    with open(f'{stab.data}/root_summary.json', 'r') as f:
        root_data = json.load(f)

    # Use root data to get list of detector configurations
    configs = sorted(root_data.keys())

    # String formatting for header, daily output, and run details
    h = f'\trun     - {"t (i3)":<7} - {"t (root)":<7} - {"events":<10} - rate'
    def day_formatter(t, n, root_fits):
        rate = 3000 if t==0 else n/t
        return f'\t{root_fits:<7} - {t:<7} - {n:<11} - {rate:.2f}'
    def run_formatter(run, t_i3, t, n):
        gb = 'b' if run in badruns else 'g'
        rate = 3000 if t==0 else n/t
        return f'\t{run}{gb} - {t_i3:<7} - {t:<7} - {n:<11} - {rate:.2f}'


    # Save rates from root and fits files
    rates = {'root':{c:{} for c in configs}, 'fits':{c:{} for c in configs}}

    # Run through each config, storing all root|fits info
    for cfg in configs:

        # Store rates and dates for rate check, cfg_info for output
        cfg_info = []

        # Run through every day present in root files
        i = 0
        for day, runs in root_data[cfg].items():

            # Root summary for the day
            cfg_info += [f'\n{day}']
            t_root = sum([run['livetime'] for r, run in runs.items()
                        if r not in badruns])
            n_root = sum([run['events'] for r, run in runs.items()
                        if r not in badruns])
            cfg_info += [day_formatter(t_root, n_root, 'root')]
            rates['root'][cfg][day] = n_root/t_root

            # Individual run summaries (from root files)
            cfg_info += [h]
            for run, info in runs.items():

                # Note if run is not in good run list
                try: t_i3 = i3_livetime[cfg][day][run]
                except KeyError:
                    print(f'{cfg} {day} Run{run} not found in good run list!')
                    t_i3 = 'N/A'

                t_root = info['livetime']
                n_root = info['events']
                cfg_info += [run_formatter(run, t_i3, t_root, n_root)]

            # Skip the fits writing part without the necessary maps
            if cfg not in fits_data.keys():
                continue

            # Note if element doesn't have fits data
            if day not in fits_data[cfg].keys():
                print(f'Warning: {day} ({cfg}) has no fits files!')
                continue

            # Fits/i3 summary for the day
            n_fits = fits_data[cfg][day]['events']
            t_i3   = fits_data[cfg][day]['livetime']
            cfg_info += [day_formatter(t_i3, n_fits, 'fits')]
            rates['fits'][cfg][day] = n_fits/t_i3

        # Save text in summary text file
        out = f'{stab.data}/{cfg}_summary.txt'
        with open(out, 'w') as outfile:
            outfile.writelines('\n'.join(cfg_info))

    # Save rate information
    out = f'{stab.data}/rates.json'
    with open(out, 'w') as f:
        json.dump(rates, f)

    print(f'Finished! Summary output saved to {stab.data}')
