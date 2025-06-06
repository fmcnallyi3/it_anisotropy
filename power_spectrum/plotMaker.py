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
            epilog = 'how to run: python [code] -f [input file path] -t [energy bin tier (1-4)] -o [ouput file path] -i [iso file] -sy [sys file] -st [stat file]')

    # File paths (Update for your use)
    p.add_argument( '-f', '--file', dest='files',
                nargs ='+', action='append', 
                default='/data/ana/CosmicRay/Anisotropy/IceTop/ITpass2/output/outpute/finalcombinedfits',
                help = 'The input file path. The default is set in a way to select tier. Please ask someone for data path if not found.')
    p.add_argument('-t', '--tier', dest='tier',
                   default = 't1',
                   help = 'The energy bin tier. please type -t t# to direct to proper directory.')
    p.add_argument('-o', '--output', dest='out',
                   default = '/data/user/ahinners/anisotropy/powerspec/Test',
                   help='output directory, please change default for your needs')
    p.add_argument('-m', '--makeErr', dest='makeError',
                   default = False,
                   action = 'store_true',
                   help = 'Determines whether or not to produce error bands/bars. Make sure to set output file path accordingly. False by default.
    p.add_argument('-i', '--iso', dest='iso',
                    nargs='+',action='append',
                    help='Input iso error bands to apply to the APS. To produce, use isoErr.py in scripts.')
    p.add_argument('-sy','--syserr',dest='sys',
                   nargs='+', action='append',
                   help='Input systematic error bars to apply to the APS. To produce, use sysErr.py in scripts.')
    p.add_argument('-st','--staterr',dest='stat',
                   nargs='+', action='append',
                   help='Input statistical error bars to apply to the APS. To produce, use statErr.py in scripts.')

    args = p.parse_args()

    # set path argument variables.
    
    file = args.files, tier = args.tier, sys = args.sys, stat = args.stat, iso = args.iso, out = ars.out

    # set tier dependent file paths
    
    if tier == 't1':
        m = f'{file}/t1/CR_IceTop__64_360_iteration04.fits.gz'
        print(m)
    else:
        m = f'{file}/{tier}/CR_IceTop__64_360_iteration20.fits.gz'
        print(m)
    
    # code to make error bands/bars. Default false.

    if makeError:

        # Make isotropic error bands
        i = f'{current}/scripts/isoErr.py -f {m} -o {out}/isoerr{tier}' 
        subprocess.Popen('nohup', i.split(' '))
        print('making isotropic error bands')
        
        # Make systematic error bars
        y = f'{current}/scripts/sysErr.py -f {m} -o {out}/syserr{tier}'
        subprocess.Popen('nohup', y.split(' '))
        print('making systematic error bars')
        
        # Make statistical error bars
        t = f'{current}/scripts/statErr.py -f {m} -o {out}/staterr{tier}'
        subprocess.Popen('nohup', t.split(' '))
        print('making statistical error bars')
        
        print('')
        print (f'error bands/bars save to {out}')
        raise

    else:
        # Code to make Angular Power Spectrum
    
        cmd = f'{current}/scripts/aps.py'
    
        a  = f'{cmd} -f {m} --syserr {sys} --staterr {stat} --iso {iso}'
        a += f' -o {out}/APS{tier} -l {label}'
        subprocess.Popen(a.split(' '))
        print( f'Angular power spectrum saved to {args.out}')