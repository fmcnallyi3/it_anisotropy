#!/bin/sh /cvmfs/icecube.opensciencegrid.org/users/juancarlos/tools/py2-v1/icetray-start
#METAPROJECT /data/user/fmcnally/offline/V04-08-00/build

import sys, os, glob, re, argparse
from glob import glob
import datetime as dt
import random
import json

from pysubmit import pysubmit


## Reprocessed data is not filtered for a good run list
def get_good_runs(grl_file, verbose=True):

    with open(grl_file, 'r') as f:
        grl_data = json.load(f)

    grl_data = grl_data['runs']

    good_runs = []
    for run in grl_data:
        if run['good_it']:
            good_runs += [run['run']]

    if verbose:
        n_good = float(len(good_runs))
        n_tot = len(grl_data)
        print('{} good runs found out of {} total ({:.1f}%)'.format(
               int(n_good), n_tot, n_good/n_tot*100))

    return good_runs



if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Makes daily healpix maps using time-scrambling code')

    # General parameters
    p.add_argument('-c', '--config', dest='config',
            help='Detector configuration [IT81-2011,IT81-2012,IT81-2013...]')
    p.add_argument('-d', '--dates', dest='dates', type=str,
            default=None, nargs='*',
            help='Dates to process [yyyymmdd] (optional, inclusive)')
    p.add_argument('-i', '--inclusive', dest='inclusive',
            default=False, action='store_true',
            help='Treat two dates given as inclusive. Otherwise treat as list')
    p.add_argument('-m', '--method', dest='method',
            default='sid',
            help='Time transformation method [sid|anti|ext|solar]')

    # Additional options
    p.add_argument('--start', dest='start',
            default=False, action='store_true',
            help='Submit the first five jobs to the cluster as a test run')
    p.add_argument('--test', dest='test',
            default=False, action='store_true',
            help='Option for running off cluster to test')
    p.add_argument('--overwrite', dest='overwrite',
            default=False, action='store_true',
            help='Option to overwrite existing map files')

    args = p.parse_args()

    ana_dir = '/data/ana/CosmicRay/Anisotropy/IceTop/twelve_year'
    root_dir = '/data/user/slehrman/burnsamplemaps'
    user = os.environ['USER']
    maps_out = '/data/user/{}/icetop_12yr/maps'.format(user)

    c_opts = vars(args).copy()
    c_opts['outDir'] = maps_out
    valid_cfgs = ['IT81-%i' % yy for yy in range(2011,2022)]
    if not args.config or args.config not in valid_cfgs:
        p.error('Invalid detector configuration')

    # Number of tiers based on detector configuration
    tiers = [3,4] if int(args.config[-4:])>=2015 else [1,2,3,4]

    # Base name for outfiles
    outBase = '{outDir}/{config}/{config}_{method}'.format(**c_opts)
    c_opts['outBase'] = outBase

    # Boost doesn't support multiple multi-parameter input options
    # Workaround: include paths to temporary file lists as text files
    batchPrefix = '/home/{}/tempFiles'.format(user)
    if not os.path.isdir(batchPrefix):
        print('Creating output directory {}'.format(batchPrefix))
        os.makedirs(batchPrefix)
    c_opts['batchFile'] = '%s/%s.txt' % (batchPrefix, os.path.basename(outBase))

    # Load good run list and save it to a file readable by TimeScramble
    grl_file = '{}/goodrunlist.json'.format(ana_dir)
    good_runs = get_good_runs(grl_file, verbose=False)
    good_runs = ['%s\n' % str(run) for run in good_runs]
    grl_file = '%s/good_runs.txt' % batchPrefix
    with open(grl_file, 'w') as f:
        f.writelines(good_runs)

    c_opts['grlFile'] = grl_file

    # Create output directories if they don't already exist
    if not os.path.isdir('{outDir}/{config}'.format(**c_opts)):
        print('Creating output directory {outDir}/{config}'.format(**c_opts))
        os.makedirs('{outDir}/{config}'.format(**c_opts))

    # Create list of desired dates
    runDates = []
    if args.dates != None and not args.inclusive:
        runDates = ['{}-{}-{}'.format(d[:4],d[4:6],d[6:8]) for d in args.dates]
    if args.dates != None and args.inclusive:
        start = dt.datetime.strptime(args.dates[0], '%Y-%m-%d')
        delta = dt.datetime.strptime(args.dates[-1], '%Y-%m-%d') - start
        runDates = [start + dt.timedelta(days=i) for i in range(delta.days+1)]
        runDates = [date.strftime('%Y-%m-%d') for date in runDates]

    # Collect input files
    fileList = []
    masterList = glob('{}/*.root'.format(root_dir))
    masterList.sort()

    # Reduce to desired detector configuration
    masterList = [f for f in masterList if f.split('_')[4] == args.config[-4:]]

    for rootFile in masterList:

        # Filter by desired dates
        date = re.findall('\d{4}_\d{4}', rootFile)[-1]
        #date = '{}-{}-{}'.format(date[:4], date[5:7], date[7:])
        #if (args.dates != None) and (date not in runDates):
        #    continue

        # Apply naming conventions to find existing files
        testFiles = [outBase]
        testFiles = ['%s_%s_Tier%i.fits' % (f, date, i) \
                for i in tiers for f in testFiles]

        # Overwrite or omit existing files
        # Files for bins are all created at once - only omit if all exist
        if all([os.path.isfile(f) for f in testFiles]) and not args.overwrite:
            continue
        for testFile in testFiles:
            if os.path.isfile(testFile):
                os.remove(testFile)

        fileList.append(rootFile)

    # Split into days for submission
    dateList = [re.findall('\d{4}_\d{4}', f)[-1] for f in fileList]
    dateList = sorted(list(set(dateList)))  # Limit to unique values

    # "Day" files are not actually 24 hours
    # Include previous and next runs (or full days when necessary)
    prev_dates, next_dates = [], []
    for date_str in dateList:
        yyyy = int(date_str[:4])
        mm = int(date_str[5:7])
        dd = int(date_str[7:])
        date = dt.datetime(yyyy, mm, dd)
        prev_dates += [(date + dt.timedelta(days=-1)).strftime('%Y_%m%d')]
        next_dates += [(date + dt.timedelta(days=1)).strftime('%Y_%m%d')]

    # Collect surrounding files to allow runs from midnight to midnight
    # ("Daily" files grouped by run, not actually 24 hours)
    dayFiles = []
    for day, prev, post in zip(dateList, prev_dates, next_dates):

        prev_files = [f for f in masterList if prev in f]
        # Reduce list of previous files to only the run right before
        #if any(['run' in f for f in prev_files]):
        #    runlist = [re.findall('run\d{6}',f)[-1] for f in prev_files]
        #    runlist = sorted(set(runlist))
        #    prev_files = [f for f in prev_files if runlist[-1] in f]

        post_files = [f for f in masterList if post in f]
        # Reduce list of next day files to only the run right after
        #if any(['run' in f for f in post_files]):
        #    runlist = [re.findall('run\d{6}',f)[-1] for f in post_files]
        #    runlist = sorted(set(runlist))
        #    post_files = [f for f in post_files if runlist[0] in f]

        one_day = [f for f in masterList if day in f]

        dayFiles += [prev_files + one_day + post_files]

    # Shortened versions for cobalt (test) or cluster (start) tests
    if args.test:
        dayFiles = dayFiles[:1]
    if args.start:
        dayFiles = dayFiles[:5]

    dayFiles = [' '.join(oneDay)+'\n' for oneDay in dayFiles]
    if args.test:
        dayFiles = [' '.join(dayFiles[0].split(' ')[:2])]

    with open(c_opts['batchFile'], 'w') as f:
        f.writelines(dayFiles)

    # Set up parameters to feed C++ script
    print('Parameters for submission:')
    validArgs  = ['config','method','outBase','batchFile','grlFile']
    c_opts = {k:v for k,v in c_opts.items() if v!=None and k in validArgs}
    for key in sorted(c_opts.keys()):
        print('  --%s %s' % (key, c_opts[key]))
    c_opts = [['--'+key, c_opts[key]] for key in sorted(c_opts.keys())]
    # Python magic: flatten list of arbitrary depth into list of strings
    flatList = lambda *n: (str(e) for a in n \
            for e in (flatList(*a) if isinstance(a, (tuple, list)) else (a,)))
    c_opts = ' '.join(list(flatList(c_opts)))

    # Increase requested memory
    sublines = ["request_memory = 4000"]

    # Environment for script
    cvmfs = '/cvmfs/icecube.opensciencegrid.org/users/juancarlos/tools/' \
            + 'py2-v1/icetray-start'
    metaproject = '/data/user/fmcnally/offline/V04-08-00/build'
    header = ['#!/bin/sh '+cvmfs, '#METAPROJECT '+metaproject]
    npx_outdir = '/home/{}/npx4_it'.format(user)
    if not os.path.isdir(npx_outdir):
        print('Creating output directory {}'.format(npx_outdir))
        os.makedirs(npx_outdir)

    # Submit files
    print('Submitting %i files...' % len(dayFiles))
    for i in range(len(dayFiles)):

        jobID = 'ts_%s_%s_%s' % (args.config, args.method, dateList[i])
        cmd  = '/home/fmcnally/icetop_12yr/time_scramble/TimeScramble'
        ex = [cmd, '--batch_idx', str(i), '--yyyymmdd', dateList[i], c_opts]
        ex = ' '.join(ex)
        print(ex)
        print('')
        pysubmit(ex, sublines=sublines, test=args.test, jobID=jobID,
                header=header, outdir=npx_outdir)
