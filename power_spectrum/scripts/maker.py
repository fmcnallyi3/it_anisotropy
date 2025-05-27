#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py3-v4.1.1/icetray-start
#METAPROJECT icetray/stable

from glob import glob
import argparse
import subprocess
import os, sys

# Import standard analysis paths from directories.py in parent directory
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from mapFunctions import directories as ani

from mapFunctions.plotFITS import medianEnergy

# Strip common (seless) info out of filename
def simplyName(f):

    base = f.split('/')[-1][:-5]
    useless = ['N10','sid']
    useful = [i for i in base.split('_') if i not in useless]
    return '_'.join(useful)


if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Standard execution protocol for power spectrum plots')
    p.add_argument('--syserr', dest='syserr',
            default=False, action='store_true',
            help='Create systematic errors for all data and w/ l=2 subtracted')
    p.add_argument('--staterr', dest='staterr',
            default=False, action='store_true',
            help='Create statistical errors for all data and w/ l=2 subtracted')
    p.add_argument('--iso', dest='iso',
            default=False, action='store_true',
            help='Create noise (isotropic) bands')
    p.add_argument('--aps', dest='aps',
            default=False, action='store_true',
            help='Create angular power spectrum')
    p.add_argument('-S', '--smooth', dest='s',
            type=float, default=0,
            help='Apply smoothing to the maps')
    p.add_argument('-m', '--multi', dest='multi',
            default=False, action='store_true',
            help='Include dipole-quadrupole subtracted version')
    p.add_argument('-n', '--n', dest='n',
            default=1000,
            help='Number of iterations for uncertainty calculations')
    args = p.parse_args()

    # Establish standard paths to analysis data
    ani.setup_input_dirs(verbose=False)
    # Establish standard paths for analysis output
    ani.setup_output_dirs(verbose=False)

     for i, f in enumerate(files):

        sName = simplyName(f)

        cmd = f'{current}/sysErr.py'
        sys_out = f'sys_{sName}_{args.n}_S{args.s}'
        a = f'{cmd} -f {f} -n {args.n} -o {ani.aps_out}/{sys_out} -S {args.s}'
        if args.syserr:
            subprocess.Popen(a.split(' '))

        cmd = f'{current}/statErr.py'
        stat_out = f'stat_{sName}_{args.n}_S{args.s}'
        a = f'{cmd} -f {f} -n {args.n} -o {ani.aps_out}/{stat_out} -S {args.s}'
        if args.staterr:
            subprocess.Popen(a.split(' '))

        cmd = f'{current}/isoErr.py'
        iso_out = f'iso_{sName}_{args.n}_S{args.s}'
        a = f'{cmd} -f {f} -n {args.n} -o {ani.aps_out}/{iso_out} -S {args.s}'
        if args.iso:
            subprocess.Popen(a.split(' '))

        cmd = f'{current}/aps.py'
        # NOTE: aps.py uses error inputs from /data/ana by default,
        # not the error outputs from above
        syserr = f'{ani.aps}/sys_{sName}_10000_S{args.s}.txt'
        staterr = f'{ani.aps}/stat_{sName}_10000_S{args.s}.txt'
        iso = f'{ani.aps}/iso_{sName}_100000_S{args.s}.npy'
        out = f'{ani.figs}/aps_{sName}_S{args.s}.pdf'
        if args.multi:
            syserr = f'{syserr} {syserr.replace(".txt", "_m2.txt")}'
            staterr = f'{staterr} {staterr.replace(".txt", "_m2.txt")}'

        a = f'{cmd} -f {f} -o {out} --staterr {staterr} --syserr {syserr} -i {iso} -l {labels[i]} -S {args.s}'
        if args.multi:
            a += ' -m'
        if args.aps:
            subprocess.Popen(a.split(' '))

