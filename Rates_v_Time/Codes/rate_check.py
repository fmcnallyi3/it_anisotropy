#!/usr/bin/env python

import argparse, json
import numpy as np
import matplotlib.pyplot as plt

import directories as stab

def main():

    # Import default project-specific paths
    stab.setup_dirs()

    p = argparse.ArgumentParser()
    p.add_argument('--rate_file', dest='rate_file',
            default=f'{stab.data}/rates.json',
            help='Json file containing rate information')
    p.add_argument('--pdiff', dest='pdiff',
            type=float, default=5,
            help='percent diff marking a significant rate change (5,10,...)')
    p.add_argument('-o', '--outdir', dest='outdir',
            default=stab.rate_plots,
            help='Output directory for plots')
    p.add_argument('--badratefile', dest='badratefile',
            default='bad_rates.csv',
            help='Output name for bad rate file')
    args = p.parse_args()


    # Rate differential
    dr = args.pdiff/100

    # Load rates from summary output
    with open(args.rate_file, 'r') as f:
        rates = json.load(f)

    # Store information on bad rates
    header = 'Configuration, Day, Source, t (i3), t (root), Events, Rate, Error'
    br_info = [header + '\n']

    # Produce rate plots for root and fits data
    for ftype in rates.keys():

        all_rates = []
        all_dates = []
        configs = sorted(rates[ftype].keys())

        for cfg in configs:

            cfg_rates = [r for day, r in rates[ftype][cfg].items()]
            cfg_dates = [day for day, r in rates[ftype][cfg].items()]
            all_rates += cfg_rates
            all_dates += cfg_dates

            # Find comparison # from median of first 7 days
            comp = np.median(cfg_rates[:7])

            for i, (day, rate) in enumerate(rates[ftype][cfg].items()):

                if (rate >= (1+dr)*comp) or (rate <= (1-dr)*comp):
                    br_info += save_info(ftype, day, cfg, comp)
                    continue

                # Include good rates into rolling average
                comp = (4*comp + rate) / 5

            # Plot rate over time
            fig, ax = plt.subplots()
            ax.plot(cfg_rates)
            ax.set_ylim(1600, 3000)

            # Adjust x-axis labels to show dates
            fig.canvas.draw()
            labels = [item.get_text() for item in ax.get_xticklabels()]
            for i in range(1, len(labels)):
                try: labels[i] = cfg_dates[int(labels[i])]
                except IndexError:
                    labels[i] = ''
            ax.set_xticklabels(labels, rotation=45, ha='right')

            # Save plot to png file
            out = f'{args.outdir}/rates_{ftype}_{cfg}.png'
            plt.savefig(out, bbox_inches="tight")
            plt.close()

        # Plot for all years
        fig, ax = plt.subplots(figsize=(20,7))
        ax.plot(all_rates)
        ax.set_ylim(1600, 3000)

        # Adjust x-axis labels to show dates
        fig.canvas.draw()
        labels = [item.get_text() for item in ax.get_xticklabels()]
        for i in range(1, len(labels)):
            try: labels[i] = all_dates[int(labels[i])]
            except IndexError:
                labels[i] = ''
        ax.set_xticklabels(labels, rotation=45, ha='right')

        out = f'{args.outdir}/rates_{ftype}_IC86.png'
        plt.savefig(out, bbox_inches="tight")
        plt.close()

    # Write bad rate information to file
    with open(f'{args.badratefile}', 'w') as f:
        f.writelines(br_info)

    print('Finished:')
    print(f'  Plots saved to {args.outdir}')
    print(f'  Bad rate information saved to {args.badratefile}')



def save_info(ftype, day, cfg, avg_rate):

    with open(f'{stab.data}/{cfg}_summary.txt', 'r') as summary:
        lines = summary.readlines()

    info = [f'{cfg},{day},,,,,,']
    overall_error = ''
    recording = False

    # Go through all lines in the appropriate summary file
    for line in lines:

        # Start recording data when the line has the target day
        if day in line:
            recording = True
            continue            # first line just has date information

        if recording:

            items = [item.strip() for item in line.split('-')]
            error_type = ''

            # Custom rearranging for root and fits summaries
            if items[0] == 'root':
                items.insert(1, '-')
            if items[0] == 'fits':
                items.insert(2, '-')
            # Skip default header
            if items[0] == 'run':
                continue

            # Automatic error classification (root files)
            if (ftype == 'root') and (items[0] not in ['root','fits']):
                rate = float(items[-1])
                t_root = int(items[2])
                if rate < avg_rate - np.sqrt(avg_rate):
                    error_type = 'Low rate'
                    if overall_error == '':
                        overall_error = 'Low rate'
                if rate > avg_rate + np.sqrt(avg_rate):
                    error_type = 'High rate'
                    if overall_error == '':
                        overall_error = 'High rate'
                if np.abs(86400 - t_root) < 10:
                    error_type = '864 error'
                    overall_error = '864 error'

            # Automatic error classification (fits files)
            if (ftype == 'fits') and (items[0] == 'fits'):
                rate = float(items[-1])
                t_i3 = int(items[1])
                if rate < avg_rate - np.sqrt(avg_rate):
                    error_type = 'Low rate'
                    overall_error = 'Low rate'
                if rate > avg_rate + np.sqrt(avg_rate):
                    error_type = 'High rate'
                    overall_error = 'High rate'

            output = ','.join(items + [error_type])
            info += [f',,{output}\n']

            # Stop recording data if the line has the word fits in it
            if 'fits' in line:
                break

    # Update summary line with error type
    info[0] += f'{overall_error}\n'

    return info


if __name__ == "__main__":

    main()
