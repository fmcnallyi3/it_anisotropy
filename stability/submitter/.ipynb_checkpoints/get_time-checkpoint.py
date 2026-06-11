#!/usr/bin/env python

import os, re, datetime

def extractTime(line, end=False):

    dateFormat = re.compile('\d{4}-\d{2}-\d{2}')
    timeFormat = re.compile('\d{2}:\d{2}:\d{2}')
    d0 = dateFormat.findall(line)[0]
    t0 = timeFormat.findall(line)[0]

    # Extract month, day, and time
    yy, mm, dd = int(d0[:4]), int(d0[5:7]), int(d0[8:])
    hrs, min, sec = int(t0[:2]), int(t0[3:5]), int(t0[6:])

    t = datetime.datetime(yy, mm, dd, hrs, min, sec)

    return t
    
    

def get_time(filename):

    if not os.path.isfile(filename):
        print('Log file {} not found'.format(filename))
        return None

    with open(filename, 'r') as f:
        lines = f.readlines()

    startLines = [line for line in lines if 'Job executing on host:' in line]
    endLines = [line for line in lines if 'Job terminated' in line or \
                'Job was aborted' in line]
    if startLines == [] or endLines == []:
        return None

    startLine = startLines[0]
    endLine = endLines[0]       # Time for last occurrence appears broken
    startTime = extractTime(startLine)
    endTime = extractTime(endLine, end=True)
    dt = endTime - startTime
    dt = dt.total_seconds()

    return dt

