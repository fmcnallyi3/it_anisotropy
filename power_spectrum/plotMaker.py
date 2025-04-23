#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py3-v4.1.1/icetray-start
#METAPROJECT: icetray/stable

import subprocess, argparse, re
import numpy as np
from glob import glob
import os, sys

current = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current)
from mapFunctions import directories as ani
from mapFunctions.plots import medianEnergy

if __name__ == "__main__":

    # General options
    p = argparse.ArgumentParser(
            description='Updated to be a wrapper script for producing Angular Power Spectrum for IceTop.')

    # Analysis plots
    p.add_argument('--powerspec', dest='powerspec',
            default=False, action='store_true',
            help='Power spectrum plot')


    # Analysis review requests
    # ...

    args = p.parse_args()

    # Load common input and output paths
    ani.setup_input_dirs(verbose=False)
    ani.setup_output_dirs(verbose=False)

    # Power spectrum 
    # Commands for making uncertainties:
    #   ./maker.py --ebins --sys -n 10000
    #   ./maker.py --ebins --stat -n 10000
    #   ./maker.py --ebins --iso -n 100000
    cmd = f'{current}/scripts/aps.py'

    # Power spectrum split by energy
    out = f'{ani.figs}/IC86_powerspec.{args.ext}'

    first = True
    for e, m in zip(energies, e_maps):

        sys = f'{ani.aps}/sys_IC86_{e}_10000_S0.txt'
        stat = f'{ani.aps}/stat_IC86_{e}_10000_S0.txt'
        iso = f'{ani.aps}/iso_IC86_{e}_100000_S0.npy'
        e_out = out.replace('powerspec', f'powerspec_{e}')
        emin, emax = e.split('-')
        emin = float(emin)
        emax = float(emax[:-3])     # Exclude the "GeV" from the name
        label = '_'.join(medianEnergy(emin, emax).split(' '))

        a  = f'{cmd} -f {m} --syserr {sys} --staterr {stat} --iso {iso}'
        a += f' -o {e_out} -l {label}'

        # Custom behavior for all plots after the first energy bin
        if not first:
            a += ' --mute_iso_labels'
        first = False

        if args.powerspec:
            proc = subprocess.Popen(a.split(' '))

print( "plots are done")
    print("All plots have been created!")



