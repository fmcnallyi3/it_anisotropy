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
## - local - copies i/o files to/from condor scratch directory (beta)      ##
## - sublines - location for additional submission options                 ##
##    - replace eventually with actual options (like 'universe')           ##
#############################################################################

import subprocess
import os, stat, random
#import numpy as np

def pysubmit(executable, jobID=None, outdir='/home/fmcnally/npx4',
              test=False, local=False, universe='vanilla',
              header=['#!/bin/bash'],
              notification='never', sublines=None):

    # Option for testing off cluster
    if test:
        os.system(executable)
        #subprocess.run(executable, check=True, shell=True)
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

    # Option to copy files to scratch directory
    ## NOTE: fails with copied i3 files (no permission to read?)
    # Input files must have '-f' argument
    if local:
        exeinfo = executable.split(' ')
        if '-f' not in exeinfo:
            raise SystemExit('Input files not preceded with "-f" argument. \
                              Cannot parse.')

        # Compile list of input files
        idx0 = exeinfo.index('-f') + 1
        idx1 = idx0
        argcheck = False
        while idx1 < len(exeinfo) and not argcheck:
            if exeinfo[idx1][0] == '-':
                argcheck = True
            else:
                idx1 += 1
        infiles = exeinfo[idx0:idx1]

        # Line to create local copies in scratch
        scratch = "${_CONDOR_SCRATCH_DIR}"
        cpFiles = 'cp %s %s' % (' '.join(infiles), scratch)
        # Change file reference in executable
        lfiles = ['%s/%s' % (scratch, os.path.basename(f)) for f in infiles]
        exeinfo[idx0:idx1] = lfiles
        executable = ' '.join(exeinfo)
        # Line to remove local copies in scratch
        rmFiles = 'rm -f %s' % ' '.join(lfiles)

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

    if local:
        exelines.insert(-3, cpFiles)
        exelines.insert(-2, rmFiles)
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
    ## REPLACE WITH ACTUAL OPTIONS FOR CONDOR SCRIPTS
    if sublines != None:
        for l in sublines:
            lines.insert(-1, '%s\n' % l)

    condor_script = '%s/2sub.sub' % outdir
    with open(condor_script, 'w') as f:
        f.writelines(lines)

    os.system('condor_submit %s' % condor_script)
