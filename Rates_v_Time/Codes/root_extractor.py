#!/usr/bin/env python

import argparse
import ROOT
from astropy.time import Time


if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Extracts and stores nEvents and livetime from ' + \
            'ROOT files, organized by each run in each day')
    p.add_argument('-i', '--infiles', dest='infiles',
            nargs='+',
            help='File(s) to retrieve the information from')
    p.add_argument('-o', '--out', dest='out',
            help='Name of output text file to store info')
    args = p.parse_args()


    # Data storage
    d = {}

    # Run through each input file
    for infile in args.infiles:

        print(f'Working on {infile}...')

        # Open root file and retrieve nEvents
        f = ROOT.TFile(infile)
        t = f.CutDST
        i = 0

        # Run through each event
        while t.GetEntry(i):

            # Note day, run, and time
            time = t.ModJulDay
            date = int(time)
            run = t.RunId
            i += 1

            # Use day as key in storage dictionary
            if date not in d.keys():
                d[date] = {}
            # Use run # as key in day sub-dictionary
            if run not in d[date].keys():
                d[date][run] = {'nEvents':0, 'stop':time, 'start':time}

            # Running count of event numbers per run
            d[date][run]['nEvents'] += 1

            # Update start and stop times for each run
            if time < d[date][run]['start']:
                d[date][run]['start'] = time
            if time > d[date][run]['stop']:
                d[date][run]['stop'] = time

    # Calculate livetime and nEvents for each run in a day
    day_info = []
    for date in d.keys():
        for run, info in d[date].items():
            ymd = Time(date, format='mjd', out_subfmt='date').iso
            livetime = int((info['stop'] - info['start'])*86400)
            day_info.append(f'{ymd} - {run} - {info["nEvents"]} - {livetime}')

    # Save information in text file
    with open(args.out, 'w') as outfile:
        outfile.writelines('\n'.join(day_info))

    print(f'Finished. Information saved to {args.out}')
