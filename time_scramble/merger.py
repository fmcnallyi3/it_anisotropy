#!/usr/bin/env python

#############################################################################
## Merges raw files to complete configuration ones (ex: all of IT73)
##############################################################################

# NOTE: update to just create IC86 merge files in addition
from __future__ import print_function

import numpy as np
import healpy as hp
import sys, os, argparse, re
from glob import glob
import datetime as dt


def calendarYear(config):

    yDict = {'IC59':2009, 'IC79':2010}
    if config in yDict.keys():
        return yDict[config]
    return int(config[-4:])


# Extract map parameters other than date and detector configuration
def mapParams(filename, rmDate=True, rmConfig=True):

    fileBase = os.path.basename(filename)   # ignore path
    mapInfo = fileBase[:-5]                 # ignore extension
    params = mapInfo.split('_')
    if rmDate:
        params = params[:-1]                # ignore date (always last)
    if rmConfig:
        params = params[1:]                 # ignore config (always first)

    return '_'.join(params)



def merger(files, out, overwrite, nmaps=3):

    # Option for overwriting existing merged file
    if os.path.isfile(out):
        if not overwrite:
            return
        os.remove(out)

    print('Working on', os.path.basename(out))
    print(len(files), 'files found...')
    if len(files) == 0:
        return

    # Merge files
    for i, f in enumerate(files):
        print('Loading {}'.format(os.path.basename(f)))
        temp = hp.read_map(f, range(nmaps), verbose=False)
        if i == 0:
            combined_map = [np.zeros(temp[j].shape) for j in range(nmaps)]
        for k in range(nmaps):
            combined_map[k] += temp[k]

    # Write to file
    hp.write_map(out, combined_map)


def projectMerge(it, prefix, omit=[], nmaps=3):

    # Get fileList for given detector
    fileList = sorted(glob('%s/merged/%s?*_N10_*.fits' % (prefix, it)))
    # Omit detector configurations (optional)
    for icyr in omit:
        fileList = [f for f in fileList if icyr not in f]

    # Merge maps with given parameters
    paramList = sorted(set([mapParams(f, rmDate=False) for f in fileList]))
    for params in paramList:
        files = [f for f in fileList if mapParams(f, rmDate=False)==params]
        out = '%s/merged/%s_%s.fits' % (prefix, it, params)
        merger(files, out, True)


if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Creates merged map files')
    p.add_argument('-c', '--configs', dest='configs', nargs='*',
            help='Specify which detector configuration (optional)')
    p.add_argument('--startDate', dest='startDate',
            default='05-13',
            help='Month and day at which to start the calendar year')
    p.add_argument('--sixyear', dest='sixyear',
            default=False, action='store_true',
            help='Recreate maps for 6-year paper')
    p.add_argument('--detectorYear', dest='detectorYear',
            default=False, action='store_true',
            help='Run using detector years instead of calendar years')
    p.add_argument('--prefix', dest='prefix',
            default='/data/user/fmcnally/anisotropy/maps',
            help='Map storage location')
    p.add_argument('--overwrite', dest='overwrite',
            default=False, action='store_true',
            help='Option to overwrite existing merged maps')
    args = p.parse_args()


    # Collect all daily map files
    masterList = sorted(glob('%s/*/*_????-??-??.fits' % args.prefix))

    # Default behavior: merge all IC86 detector configurations
    if args.configs == None and not args.sixyear:
        masterList = [f for f in masterList if 'IC86' in f]
        configs = [re.findall('IC86-\d{4}',f)[0] for f in masterList]
        args.configs = sorted(set(configs))

    for cfg in args.configs:

        fileList = []

        if args.sixyear or args.detectorYear:
            fileList += [f for f in masterList if cfg in f]

        else:
            yyyy = calendarYear(cfg)
            s = '%i-%s' % (yyyy, args.startDate)
            e = '%s-%s' % (yyyy+1, args.startDate)
            start = dt.datetime.strptime(s, '%Y-%m-%d')
            end = dt.datetime.strptime(e, '%Y-%m-%d')
            delta = end - start
            runDates = [start+dt.timedelta(days=i) for i in range(delta.days)]
            for date in runDates:
                d = date.strftime('%Y-%m-%d')
                fileList += [f for f in masterList if d in f]

        fileList.sort()

        # Calculate comprehensive list of all unique parameters
        paramList = sorted(set([mapParams(f) for f in fileList]))

        # Run merger on each set of parameters
        for params in paramList:
            files = [f for f in fileList if mapParams(f)==params]
            out = '%s/merged/%s_%s.fits' % (args.prefix, cfg, params)
            merger(files, out, args.overwrite)

    # Run project merger
    detectorList = ['IC86']
    omit = []
    if args.sixyear:
        detectorList = ['IC']
        omit = ['IC86_'] + ['IC86-%i' % i for i in range(2015,2020)]
    for detector in detectorList:
        projectMerge(detector, args.prefix, omit=omit)


