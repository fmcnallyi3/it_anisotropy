#!/usr/bin/env python
# coding: utf-8

#imports needed packages
import healpy as hp
import numpy as np
import argparse

import os, sys

# Import standard analysis paths from directories.py in parent directory
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from map_functions import getMap, multi_subtraction

if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Makes angular power spectrum statistical error bars.',
            epilog='To run: python [code] -f [path to input file] -o [path to output file]. Optional: -n can be set to any integer and is defaulted to 1e5.')
    p.add_argument('-f', '--files', dest='files',
            nargs='+',
            help='Input filenames. Use -f flag for each set of files.')
    p.add_argument('-n', '--n', dest='n',
            type=int,
            default = int(1e5),
            help='Number of simulated power spectra to generate.')
    p.add_argument('-s', '--smooth', dest='smooth',
            type=float, default=0,
            help='Smooth data and background maps')
    p.add_argument('-o', '--out', dest='out',
            help='Output filename.')

    args = p.parse_args()

    # Avoid boosted counts if top-hat smoothing applied
    norm = True if args.smooth!=0 else False

    # Calculate for maps with/out multipole fit subtraction
    for multi in [False, 2]:

        # Data and background maps for calculating relative intensity
        dataMap = getMap(args.files, mapName='data', mask=True, 
                smooth=args.smooth, norm=norm)
        dataMap[dataMap==hp.UNSEEN] = 0
        bgMap = getMap(args.files, mapName='bg', mask=True, 
                smooth=args.smooth, norm=norm)
        bgMap[bgMap==hp.UNSEEN] = 0

        # Normalized version of bg map used for weighting
        weight = bgMap / bgMap[bgMap!=0].mean()

        # Map paramaters
        npix = bgMap.size
        nside = hp.npix2nside(npix)
        lmax = 3*nside - 1

        # Generate fake maps, calculate power spectra, and store
        fakeCl = np.zeros((args.n, lmax+1))

        for n in range(args.n):

            # Wiggle isotropic map within poisson uncertainties
            dummyMap = np.random.poisson(dataMap)
            if multi != False:
                dummyMap = multi_subtraction(multi, dummyMap, bgMap)

            # Calculate relative intensity
            relint = (dummyMap/bgMap - 1)
            relint[relint!=relint] = 0      # deal with NaN's

            # Weight, shift, calculate power spectrum
            relint_w = relint * weight
            relint_w -= np.average(relint_w)

            fakeCl[n] = hp.anafast(relint_w, lmax=lmax)


        # Calculate 1-sigma containment values from simulated Cls
        lims = [16, 50, 84]
        s_16, s_50, s_84 = np.percentile(fakeCl, lims, axis=0)
        dCl = [ s_50-s_16, s_84-s_50 ]

        # Save as dictionary
        out = f'{args.out}'
        if multi != False:
            out += f'_m{multi}'
        np.savetxt(f'{out}.txt', dCl)
        print(f'Statistical errorbars written to {out}.txt')



