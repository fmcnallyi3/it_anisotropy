#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py3-v4.1.1/icetray-start
#METAPROJECT: icetray/stable

import argparse
import subprocess
import os

current = os.path.dirname(os.path.realpath(__file__))

if __name__ == "__main__":

    # General options
    p = argparse.ArgumentParser(
            description='Wrapper script for producing Angular Power Spectrum for IceTop.',
            epilog = 'How to run: python [code] -f [input file path] -t [energy bin tier (1-4)] -o [ouput file path] -l [plot labels] -S [smoothing angle]. Use -m to make the uncertainty files (make these first).')

    # File paths (Update for your use)
    p.add_argument( '-f', '--file', dest='files',
                nargs ='+', action='append',
                default='/data/ana/CosmicRay/Anisotropy/IceTop/ITpass2/output/outpute/finalcombinedfits',
                help = 'The input file path. The default is set in a way to select tier. Please ask someone for data path if not found.')
    p.add_argument('-t', '--tier', dest='tier',
                   default = 't1',
                   help = 'The energy bin tier. please type -t t# to direct to proper directory. default t1.')
    p.add_argument('-o', '--output', dest='out',
                   default = '/data/user/ahinners/anisotropy/powerspec/Test',
                   help='output directory, please change default for your needs')
    p.add_argument('-m', '--makeErr', dest='makeError',
                   default = False,
                   action = 'store_true',
                   help = 'Determines whether or not to produce error bands/bars. May take a long time to complete. False by default.')
    p.add_argument('-nI', dest='nI',
                   type=int,
                   help='How many times do you want to iterate the isotropic noise bands? default is 1e6.')
    p.add_argument('-nS', dest='nS',
                   type=int,
                   help='How many times do you want to iterate the systematic/statistical error bars? default is 1e5')
    p.add_argument('-S', '--smooth', dest='smooth',
                   type=float, default=0,
                   help='Smooth data and background maps.')
    p.add_argument('-l', '--label', dest='label',
                   nargs='+',
                   help='Sets the label for the plot legend.')


    args = p.parse_args()

    # set path argument variables.

    file = args.files
    tier = args.tier
    smooth = args.smooth
    label = args.label
    out = args.out

    # set tier dependent file paths

    if tier == 't1':
        f = f'{file}/t1/CR_IceTop__64_360_iteration04.fits.gz'
    else:
        f = f'{file}/{tier}/CR_IceTop__64_360_iteration20.fits.gz'

    # code to make error bands/bars. Default false.

    if args.makeError:

        # Make isotropic error bands
        cmdi = f'{current}/scripts/isoErr.py'
        i = f'{cmdi} -f {f} -S {smooth} -o {args.out}/{args.tier}iso'

        print(i.split())
        print(type(i[2].split()))

        subprocess.Popen(i.split(' '))
        print('making isotropic noise bands')

        # Make systematic error bars
        cmdy = f'{current}/scripts/sysErr.py'
        y = f'{cmdy} -f {f} -S {smooth} -o {out}/{tier}sys'
        #print(y)
        subprocess.Popen(y.split(' '))
        print('making systematic error bars')

        # Make statistical error bars
        cmdt = f'{current}/scripts/statErr.py'
        t = f'{cmdt} -f {f} -S {smooth} -o {out}/{tier}stat -n 100'
        #print(t)
        subprocess.Popen(t.split(' '))
        print('making statistical error bars')

        print('')
        print(f'The error bands/bars were saved to {out}')

    else:
        # Code to make Angular Power Spectrum

        cmd = f'{current}/scripts/aps.py'

        # set arguments for uncertainty files (the out directory is where the files are too)
        iso = f'{out}/{tier}iso.npy'
        sys = f'{out}/{tier}sys.txt'
        stat = f'{out}/{tier}stat.txt'

        a  = f'{cmd} -f {f} -sy {sys} -st {stat} -i {iso}'
        a += f' -o {out}/APS{tier} -l {label}'
        subprocess.Popen(a.split(' '))
        print(f'Angular power spectrum saved to {args.out}')
