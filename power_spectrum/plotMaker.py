#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py3-v4.4.2/icetray-start
#METAPROJECT: icetray/stable

import argparse
import subprocess
import glob
from pathlib import Path

current = Path.cwd()

if __name__ == "__main__":

    # General options
    p = argparse.ArgumentParser(
            description='Wrapper script for producing Angular Power Spectrum for IceTop.',
            epilog = 'How to run: python [code] -f [input file path] -t t[energy bin tier (1-4)] -o [ouput file path] -l [plot labels] -s [smoothing angle]. Use -m to make the uncertainty files, use -i, -st, or -sy to specify which uncertainty to make. use -n to iterate the uncertainties (more iterations -> better stats).')

    # File paths (Update for your use)
    p.add_argument( '-f', '--inFile', dest='inFiles',
                default='/data/ana/CosmicRay/Anisotropy/IceTop/ITpass2/output/outpute/finalcombinedfits',
                help = 'The input file path. The default is set in a way to select tier. Please ask someone for data path if not found.')
    p.add_argument('-t', '--tier', dest='tier',
                   default = '1',
                   help = 'The energy bin tier. please type -t # to direct to proper directory. default 1.')
    p.add_argument('-o', '--output', dest='out',
                   default = '/data/user/ahinners/anisotropy/powerspec',
                   help='output directory, please change default for your needs')
    p.add_argument('-m', '--make', dest='make',
                   default = False,
                   action = 'store_true',
                   help = 'Determines whether or not to produce the angular power spectrum.')
    p.add_argument('-n','--n', dest='n',
                   type=int,
                   help='Determines how many times the uncertainty iterates. Default iso = 1e6, default sys/stat = 1e5.')
    p.add_argument('-i', '--iso', dest='iso',
                   default = False,
                   action = 'store_true',
                   help = 'Makes the isotropic noise bands')
    p.add_argument('-sy', '--sysErr', dest = 'sys',
                   default = False,
                   action = 'store_true',
                   help = 'Makes the systematic error bars.')
    p.add_argument('-st','--statErr',dest = 'stat',
                   default = False,
                   action = 'store_true',
                   help = 'Makes the statistical error bars.')
    p.add_argument('-s', '--smooth', dest='smooth',
                   type = float, default = 0,
                   help = 'Smooth data and background maps.')
    p.add_argument('-l', '--label', dest='label',
                   nargs='+',
                   help='Sets the label for the plot legend.')
    p.add_argument('-il', '--iso_label', dest='iso_label',
                   default=False, action='store_true',
                   help='Suppress the output of noise labels in legend')
    p.add_argument('-icp', '--ice_prelim', dest='icp',
                   default=False, action ='store_true',
                   help='Adds IceCube Preliminary to power spectrum')

    args = p.parse_args()

    # find the final iteration for our tier

    file_list = sorted(glob.glob(f'{args.inFiles}/t{args.tier}/CR_IceTop__64_360_iteration*'))
    f = file_list[-1]

    # Make isotropic error bands
    cmd = f'{current}/scripts/isoErr.py'
    a = f'{cmd} -f {f} -s {args.smooth} -o {args.out}/T{args.tier}/t{args.tier}iso' 
    
    if args.iso:
        subprocess.Popen(a.split(' '))
        print('making isotropic noise bands')
    
    # Make systematic error bars
    cmd = f'{current}/scripts/sysErr.py'
    a = f'{cmd} -f {f} -n {args.n} -s {args.smooth} -o {args.out}/T{args.tier}/t{args.tier}sys'

    if args.sys:
        subprocess.Popen(a.split(' '))
        print('making systematic error bars')
    
    # Make statistical error bars
    cmd = f'{current}/scripts/statErr.py'
    a = f'{cmd} -f {f} -n {args.n} -s {args.smooth} -o {args.out}/T{args.tier}/t{args.tier}stat'

    if args.stat:
        subprocess.Popen(a.split(' '))
        print('making statistical error bars')

    if (args.iso or args.sys or args.stat):
        print(f'The uncertainties were saved to {args.out}/T{args.tier}')

    # Code to make Angular Power Spectrum
    if args.make:
        cmd = f'{current}/scripts/aps.py'
        
        # set arguments for uncertainty files (the out directory is where the files are too)
        iso_file = Path(f'{args.out}/T{args.tier}/t{args.tier}iso.npy')
        sys_file = Path(f'{args.out}/T{args.tier}/t{args.tier}sys.txt')
        stat_file = Path(f'{args.out}/T{args.tier}/t{args.tier}stat.txt')

        # Check if an uncertainty file is present, if it is, add it to the graph
        a  = f'{cmd} -f {f} '
        if iso_file.is_file():
            a += f'-i {iso_file} '
        if sys_file.is_file():
            a += f'-sy {sys_file} '
        if stat_file.is_file():
            a += f'-st {stat_file} '
        if args.iso_label:
            a += f'-il '
        if args.icp:
            a += f'-icp '
    
        a += f'-s {args.smooth} -o {args.out}/T{args.tier}/APS_T{args.tier}_S{args.smooth} -l {args.label}'
        subprocess.Popen(a.split(' '))

        print(f'Angular power spectrum saved to {args.out}/T{args.tier}')
