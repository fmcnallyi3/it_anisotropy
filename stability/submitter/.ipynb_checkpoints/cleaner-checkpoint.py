#!/usr/bin/env python

#######################################################
# Runs through error files, returns a list of files where the process ran
# correctly, and can remove files associated with good runs
#######################################################

import os, sys, re, argparse
from glob import glob

from pathlib import Path

from get_time import get_time


# List of any safe errors you want to ignore
def get_error_list():
    safe_errors = []
    safe_errors.append('Error in <TSystem::ExpandFileName>: input: $HOME/.root.mimes, output: $HOME/.root.mimes')
    return safe_errors


def good_file(filename, strict):

    # Check the error file for any lines that aren't harmless
    with open(filename, 'r') as f:
        err = f.readlines()
        err = [l.strip() for l in err]

    # Remove non-error-related I3Tray output
    oks = ['NOTICE','INFO','WARN']
    err = [l for l in err if l.split(' ')[0] not in oks]
    # Option: ignore all lines that don't explicity list as "Error"
    if strict:
        err = [l for l in err if any([e in l for e in ['error','Error']])]

    safe_errors = get_error_list()
    if any([l not in safe_errors for l in err]):
        return False

    return True


def resubmit(npxdir, jobID):

    ## NOTE: Assumes the last jobs you submitted involved the same options
    ## (example: request_memory), and that the sub script is '2sub.sub'

    # Condor submission script
    d = {}
    d['executable'] = '%s/npx4-execs/%s.sh\n' % (npxdir, jobID)
    d['log'] = '%s/npx4-logs/%s.log\n' % (npxdir, jobID)
    d['output'] = '%s/npx4-out/%s.out\n' % (npxdir, jobID)
    d['error'] = '%s/npx4-error/%s.error\n' % (npxdir, jobID)

    with open('2sub.sub','r') as f:
        lines = f.readlines()

    for key in d.keys():
        for i, l in enumerate(lines):
            if l.split(' ')[0].lower() == key:
                lines[i] = '%s = %s' % (key, d[key])
        # Remove all log, output, and error files before resubmitting
        if os.path.isfile(d[key].strip()) and 'exec' not in key:
            print(f'File {d[key]} found! Removing...')
            os.remove(d[key].strip())

    with open('2sub.sub', 'w') as f:
        f.writelines(lines)

    os.system('condor_submit %s' % '2sub.sub')



if __name__ == "__main__":

    # Get absolute path to current directory
    script_path = Path(__file__).resolve()
    submit_dir = script_path.parent

    parser = argparse.ArgumentParser(
            description='Scan npx4 files and remove good runs')
    parser.add_argument('--npxdir', dest='npxdir',
            default=submit_dir,
            help='Location of npx4 folders')
    parser.add_argument('--purge', dest='purge',
            default=False, action='store_true',
            help='Remove all npx4 files')
    parser.add_argument('--strict', dest='strict',
            default=False, action='store_true',
            help='ONLY look at lines with the word "Error" in them')
    parser.add_argument('--badInfo', dest='badInfo',
            default=False, action='store_true',
            help='Print bad output lines')
    parser.add_argument('--rerun', dest='rerun',
            default=False, action='store_true',
            help='Rerun bad run files')
    parser.add_argument('--orphans', dest='orphans',
            default=False, action='store_true',
            help='Mark orphaned executable files as bad')
    parser.add_argument('-v', '--verbose', dest='verbose',
            default=False, action='store_true',
            help='Give additional print output')
    args = parser.parse_args()

    # List of all npx4 files and jobIDs
    files = glob('%s/npx4-*/*' % args.npxdir)
    jobIDs = sorted(set([re.split('/|\.', f)[-2] for f in files]))

    # Input function dependent on python version
    inFunc = input if sys.version_info.major == 3 else raw_input

    # Rerun option
    if args.rerun:
        yn = inFunc('Rerun all bad and held executables? [y/N]: ')
        if yn != 'y':
            print('Rerun canceled. Aborting...')
            sys.exit(0)

    # Purge option
    if args.purge:
        yn = inFunc('Purge all %i npx4 files? [y/N]: ' % len(files))
        if yn == 'y':
            for f in files:
                os.remove(f)
        else:
            print('Purge canceled')
        sys.exit(0)

    good, bad, held, orphans, abort, tList = [],[],[],[],[],[]
    t = 0.

    for jobID in jobIDs:

        # Unstarted jobs will not have output files
        exe = '{}/npx4-execs/{}.sh'.format(args.npxdir, jobID)
        out = '{}/npx4-out/{}.out'.format(args.npxdir, jobID)
        err = '{}/npx4-error/{}.error'.format(args.npxdir, jobID)
        log = '{}/npx4-logs/{}.log'.format(args.npxdir, jobID)

        # All jobs should have an exe and a log file
        if not os.path.isfile(exe) or not os.path.isfile(log):
            orphans.append(jobID)
            continue

        # User-aborted cases should register separately
        with open(log, 'r') as f:
            lines = f.readlines()
        if any(['Job was aborted' in l for l in lines]) and \
                not any(['Job was held' in l for l in lines]):
            abort.append(jobID)
            continue

        # Jobs that have not yet begun won't have a .out file
        if not os.path.isfile(out):
            continue

        # Optionally print which files are missing
        npxfiles = [out, err, log]
        if args.verbose:
            for npxfile in npxfiles:
                if not os.path.isfile(npxfile):
                    print('{} not found for {}'.format(npxfile, jobID))

        # Mark orphaned files
        if not all([os.path.isfile(f) for f in npxfiles]):
            orphans.append(jobID)
            continue

        # Mark held jobs
        with open(log, 'r') as f:
            lines = f.readlines()
        log_messages = ['Job was held', 'Job was evicted']
        if any([m in l for l in lines for m in log_messages]) and \
                not any(['Normal termination' in l for l in lines]):
            if any(['Job was aborted' in l for l in lines]):
                held.append(jobID)
            continue

        # Make sure there's some text in the output file
        with open(out, 'r') as f:
            lines = f.readlines()
        if lines == []:
            print('{} is empty!'.format(out))
            continue

        # Check the error file for any lines that aren't harmless
        is_good = good_file(err, args.strict)

        # Append run number to good or bad run list
        t0 = get_time(log)
        if t0 == None:
            # Missing a start or end time (still running)
            continue
        if is_good:
            good.append(jobID)
            t += t0
            tList += [t0]
        else:
            bad.append(jobID)

    # Print information on state of npx4 files
    nFinished = len(good) + len(bad) + len(orphans) + len(held) + len(abort)
    nRunning = len(jobIDs) - nFinished
    if nRunning != 0:
        print('Running (%i file(s)):' % nRunning)
        for jobID in jobIDs:
            if all([jobID not in r for r in good+bad+orphans+held+abort]):
                print('  - %s' % jobID)
        print('')

    # Good runs
    if len(good) != 0 and not args.badInfo:
        print('Good runs (%i file(s)):' % len(good))
        for jobID in good:
            print(' --- %s ---' % jobID)
        print('  Average time per job: %.01f seconds' % (t/len(good)))
        tList.sort()
        print('    Min time: %.01f' % tList[0])
        print('    Max time: %.01f' % tList[-1])
        print('')

    # Orphaned runs
    if len(orphans) != 0 and not args.badInfo:
        print('Orphaned runs (%i file(s)):' % len(orphans))
        for jobID in orphans:
            print(' --- %s ---' % jobID)
        print('')

    # Held runs
    if len(held) != 0 and not args.badInfo:
        print('Held runs (%i file(s)):' % len(held))
        for jobID in held:
            print(' --- %s ---' % jobID)

            # Option to resubmit failed executables
            if args.rerun:
                resubmit(args.npxdir, jobID)

        print('')

    # User-aborted runs
    if len(abort) != 0 and not args.badInfo:
        print('User-aborted runs (%i file(s)):' % len(abort))
        for jobID in abort:
            print(' --- %s ---' % jobID)

            # Option to resubmit aborted executables
            if args.rerun:
                resubmit(args.npxdir, jobID)

        print('')

    # Bad runs
    if len(bad) != 0:
        print('Bad runs (%i file(s)):' % len(bad))
        for jobID in bad:
            print(' --- %s ---' % jobID)

            # Option to print detailed information for each file
            if args.badInfo:
                err = '%s/npx4-error/%s.error' % (args.npxdir, jobID)
                with open(err, 'r') as f:
                    lines = f.readlines()
                for l in lines:
                    try:
                        if l.split()[0] not in ['NOTICE','INFO','WARN','\n']:
                            print('    %s' % l.strip())
                    except IndexError:
                        continue
                print()

            # Option to resubmit failed executables
            if args.rerun:
                resubmit(args.npxdir, jobID)

        print('')

    # Option to remove good runs
    if len(good) != 0 and not args.badInfo and not args.rerun:
        yn = inFunc('Do you want to remove the good runs? [y/N]: ')
        if yn == 'y':
            for jobID in good:
                rmFiles = glob('%s/npx4-*/%s.*' % (args.npxdir, jobID))
                for f in rmFiles:
                    os.remove(f)


##===========================================================================##
## Relic code
##

## For reading information from condor_q output
##  user = getpass.getuser()
##  bashCommand = 'condor_q %s -wide' % user
##  process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
##  output = process.communicate()[0]
##  output = [i.strip() for i in output.split('\n')]
##
##  print(output)
##
##  # Make sure call to condor went correctly
##  # Fails with new update. Check later
##  for phrase in ['jobs','completed','removed','idle','running','held']:
##      if phrase not in output[-2]:
##          print('Fetch from condor failed')
##          return []
##  #0 jobs; 0 completed, 0 removed, 0 idle, 0 running, 0 held, 0 suspended

##===========================================================================##

