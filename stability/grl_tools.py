#!/usr/bin/env python

import json
import urllib
from urllib.request import Request
from urllib.request import urlopen
from urllib.parse import urlencode
import ssl
from urllib.error import HTTPError 

from datetime import datetime as dt
from collections import defaultdict


''' Extract good run list from i3live '''
def i3live_grl(start, end, icetop=False):

    url = 'https://live.icecube.wisc.edu/snapshot-export/'

    # Start and end can be runs (integers) or dates (yyyy-mm-dd HH:MM:SS)
    rd = 'run' if type(start)==int else 'date'
    params = {'user': 'icecube',
          'pass': 'skua',
          f'start_{rd}': start,
          f'end_{rd}': end}


    # Fetch the JSON data (hits the database)
    data = urlencode(params).encode('utf-8')
    req = Request(url)
    try:
        context = ssl._create_unverified_context()
        response = urlopen(req, data=data, context=context).read()
    except HTTPError as err:
        if err.code == 404:
            raise I3LiveException('Invalid run number')
        elif err.code == 403:
            raise I3LiveException('Not authorized')
        raise I3LiveException(f'Error {err.code} loading URL {url}.')



    # Parse JSON into a python dict and print some of it
    d = json.loads(response)
    goodruns = []
    is_good = 'good_it' if icetop else 'good_i3'
    for r in d['runs']:
        if r[is_good]:
            goodruns.append(r)

    return goodruns


''' Parse Seraps good run list for IceTop '''
def parse_seraps_GRL(grl_file):

    # Object to return
    goodruns = []

    # Default indices for data
    good_idx = 1    # Good_it
    ymd_idx  = 6    # OutDir (has date information)
    t_idx    = 2    # LiveTime

    # Indices different for IC86_2011
    if 'IC86_2011' in grl_file:
        good_idx = 3
        ymd_idx  = 8
        t_idx    = 4

    # Read and parse the GRL
    with open(grl_file, 'r') as f:
        data = f.readlines()

    for line in data:

        items = line.split()
        r = {}

        # Look out for empty lines (happens once in 2011)
        if len(items) == 0:
            continue

        # Collect information on good runs
        if items[0].isdigit() and int(items[good_idx])==1:

            ymd_info = items[ymd_idx].split("/")
            year = ymd_info[4]
            month = ymd_info[7][:2]
            day = ymd_info[7][-2:]
            r['date'] = f'{year}-{month}-{day}'
            r['run'] = int(items[0])
            r['livetime'] = items[t_idx]

            goodruns.append(r)

    return goodruns



''' Convert good run information into a dictionary with daily livetime '''
def daily_livetime(i3_goodruns, it_goodruns=[]):

    # Create dict with format: i3_livetime[day][run] = livetime
    i3_livetime = defaultdict(lambda: defaultdict(int))

    # IceTop requires additional check that runs exist in Serap's GRL
    if len(it_goodruns) != 0:
        it_runvals = [r['run'] for r in it_goodruns]
        n0 = len(i3_goodruns)
        i3_goodruns = [r for r in i3_goodruns if r['run'] in it_runvals]
        n1 = len(i3_goodruns)
        print(f'{(n0-n1)/n0 * 100:.1f}% of runs filtered out by IT GRL')

    # Convert runs into a dictionary with keys for day and run
    for run_info in i3_goodruns:

        # Instate each day as a key for the dictionary
        day = run_info['good_tstart'].split(' ')[0]
        run = run_info['run']

        # Obtain start/stop times from list, removing fractions of seconds
        t_i = run_info['good_tstart'].split('.')[0]
        start_t = dt.strptime(t_i, '%Y-%m-%d %H:%M:%S')
        t_f = run_info['good_tstop'].split('.')[0]
        stop_t = dt.strptime(t_f, '%Y-%m-%d %H:%M:%S')

        # Check if run crosses over a day and adjust start/stop times
        if start_t.day != stop_t.day:
            day_next = stop_t.strftime('%Y-%m-%d')
            midnight = dt.combine(stop_t, dt.min.time())
            i3_livetime[day][run] = (midnight - start_t).seconds
            i3_livetime[day_next][run] = (stop_t - midnight).seconds

        # If no crossover, the run is fully contained in a day
        else:
            i3_livetime[day][run] = (stop_t - start_t).seconds

    return i3_livetime
