#!/usr/bin/env python

#############################################################################
## A python wrapper for submitting executables. To use, import pysubmit    ##
## and call in a python script.                                            ##
##                                                                         ##
## Arguments:                                                              ##
## - executable - string with the executable argument                        ##
##    - ex: '/home/user/test.py -a [argument]'                             ##
## - jobID - title for the job in condor and exec/out/log/error files      ##
## - outdir - location for exec/out/log/error files                        ##
## - test - run executable off cluster as a test                           ##
## - sublines - location for additional submission options                 ##
##    - replace eventually with actual options (like 'universe')           ##
#############################################################################


import os, stat, random
from pathlib import Path


def pysubmit(executable, jobID=None, outdir=None,
              test=False, universe='vanilla',
              header=['#!/bin/bash'],
              notification='never', sublines=None):

    # Default output path = parent directory for this file
    if outdir == None:
        script_path = Path(__file__).resolve()
        outdir = script_path.parent

    # Option for testing off cluster
    if test:
        os.system(executable)
        quit()
        return

    # Default naming for jobIDs if not specified
    if jobID == None:
        jobID = 'npx4-%05d' % random.uniform(0, 100000)

    # Ensure output directories exist
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    for condorOut in ['execs','logs','out','error']:
        if not os.path.isdir('%s/npx4-%s' % (outdir, condorOut)):
            os.mkdir('%s/npx4-%s' % (outdir, condorOut))

    # Create execution script
    exelines = header + [
        "date",
        "hostname",
        "",
        "%s" % executable,
        "",
        "date",
        "echo 'Fin'"
    ]

    exelines = [l+'\n' for l in exelines]

    outexe = '%s/npx4-execs/%s.sh' % (outdir, jobID)
    with open(outexe, 'w') as f:
        f.writelines(exelines)

    # Make file executable
    st = os.stat(outexe)
    os.chmod(outexe, st.st_mode | stat.S_IEXEC)

    # Condor submission script
    lines = [
        "universe = %s" % universe,
        "executable = %s/npx4-execs/%s.sh" % (outdir, jobID),
        "log = %s/npx4-logs/%s.log" % (outdir, jobID),
        "output = %s/npx4-out/%s.out" % (outdir, jobID),
        "error = %s/npx4-error/%s.error" % (outdir, jobID),
        "notification = %s" % notification,
        "queue"
    ]
    lines = [l+'\n' for l in lines]

    # Option for additional lines to submission script
    if sublines != None:
        for l in sublines:
            lines.insert(-1, '%s\n' % l)

    condor_script = '%s/2sub.sub' % outdir
    with open(condor_script, 'w') as f:
        f.writelines(lines)

    os.system('condor_submit %s' % condor_script)
