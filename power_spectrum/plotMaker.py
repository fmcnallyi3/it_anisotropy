#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py3-v4.1.1/icetray-start
#METAPROJECT: icetray/stable

import subprocess, argparse, re
import numpy as np
from glob import glob
import os, sys

current = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current)

if __name__ == "__main__":

    # General options
    p = argparse.ArgumentParser(
            description='Updated to be a wrapper script for producing Angular Power Spectrum for IceTop.',
            epilog = 'How to run: python [code] -f [input file path] -t [energy bin tier (1-4)] -o [ouput file path] -i [iso file] -sy [sys file] -st [stat file] -l [plot labels]')

    # File paths (Update for your use)
    p.add_argument( '-f', '--file', dest='files',
                nargs ='+', action='append', 
                default='/data/ana/CosmicRay/Anisotropy/IceTop/ITpass2/output/outpute/finalcombinedfits',
                help = 'The input file path. The default is set in a way to select tier. Please ask someone for data path if not found.')
    p.add_argument('-t', '--tier', dest='tier',
                   default = 't1',
                   help = 'The energy bin tier. please type -t t# to direct to proper directory. defaule t1.')
    p.add_argument('-o', '--output', dest='out',
                   default = '/data/user/ahinners/anisotropy/powerspec/Test',
                   help='output directory, please change default for your needs')
    p.add_argument('-m', '--makeErr', dest='makeError',
                   default = False,
                   action = 'store_true',
                   help = 'Determines whether or not to produce error bands/bars. May take a long time to complete. False by default.')
    p.add_argument('-i', '--iso', dest='iso',
                    nargs='+',action='append',
                    help='Input iso error bands to apply to the APS. To produce, use isoErr.py in scripts.')
    p.add_argument('-sy','--syserr',dest='sys',
                   nargs='+', action='append',
                   help='Input systematic error bars to apply to the APS. To produce, use sysErr.py in scripts.')
    p.add_argument('-st','--staterr',dest='stat',
                   nargs='+', action='append',
                   help='Input statistical error bars to apply to the APS. To produce, use statErr.py in scripts.')
    p.add_argument('-l', '--label', dest='label',
                   nargs='+',
                   help='Sets the label for the plot legend')
    

    args = p.parse_args()

    # set path argument variables.
    
    file = args.files 
    tier = args.tier 
    sys = args.sys
    stat = args.stat 
    iso = args.iso
    label = args.label
    out = args.out
    data = f'/data/user/ahinners/anisotropy/powerspec/'
    
    # set tier dependent file paths
    
    if tier == 't1':
        m = f'{file}/t1/CR_IceTop__64_360_iteration04.fits.gz'
    else:
        m = f'{file}/{tier}/CR_IceTop__64_360_iteration20.fits.gz'
    
    # code to make error bands/bars. Default false.

    if args.makeError:

        # Make isotropic error bands
        cmdi = f'{current}/isoErr.py'
        i = f'{cmdi} -f {m} -o {out}{tier}iso -n 100' 
        subprocess.Popen(i.split(), shell=True)
        print('making isotropic noise bands')
        
        # Make systematic error bars
        cmdy = f'{current}/sysErr.py'
        y = f'{cmdy} -f {m} -o {out}{tier}sys -n 100'
        subprocess.Popen(y.split(), shell=True)
        print('making systematic error bars')
        
        # Make statistical error bars
        cmdt = f'{current}/statErr.py'
        t = f'{cmdt} -f {m} -o {out}{tier}stat -n 100'
        subprocess.Popen(t.split(), shell=True)
        print('making statistical error bars')
        
        print('')
        print(f'The error bands/bars were saved to {out}')

    else:
        # Code to make Angular Power Spectrum
    
        cmd = f'{current}/aps.py'
        iso = f'{data}/{tier}/
    
        a  = f'{cmd} -f {m} -sy {sys} -st {stat} -i {iso}'
        a += f' -o {out}/APS{tier} -l {label}'
        subprocess.Popen(a.split())
        print(f'Angular power spectrum saved to {args.out}')