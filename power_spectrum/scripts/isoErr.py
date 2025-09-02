#!/usr/bin/env python
# coding: utf-8

import healpy as hp
import numpy as np
import argparse

import os, sys

# Import standard analysis paths from directories.py in parent directory
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from map_functions import getMap, maskMap


if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Makes angular power spectrum isotropic bands.',
            epilog='To run: python [code] -f [path to input file] -o [path to output file]. -n can be set to any integer and is defaulted to 1e6')
    p.add_argument('-f', '--files', dest='files',
            nargs='+',
            help='Input filenames. Use -f flag for each set of files.')
    p.add_argument('-n', '--n', dest='n',
            type=int, default=int(1e6),
            help='Number of simulated power spectra to generate.')
    p.add_argument('-s', '--smooth', dest='smooth',
            type=float, default=0,
            help='Smooth data and background maps')
    p.add_argument('-o', '--out', dest='out',
            help='Output filename.')

    args = p.parse_args()

    # Avoid boosted counts if top-hat smoothing applied
    norm = True if args.smooth!=0 else False

    # Background map should represent detector response to isotropic sky
    bgMap = getMap(args.files, mapName='bg', mask=True, 
                   smooth=args.smooth, norm=norm)
    bgMap[bgMap==hp.UNSEEN] = 0
    #bgMap /= 33

    # "Normalize" by dividing by average value of unmasked pixels
    weight = bgMap / bgMap[bgMap!=0].mean()

    # Map paramaters
    npix = bgMap.size
    nside = hp.npix2nside(npix)
    lmax = 3*nside - 1

    # Generate fake maps, calculate power spectra, and store
    fakeCl = np.zeros((args.n, lmax+1))
    for n in range(args.n):

        # Wiggle isotropic map within poisson uncertainties
        dummyMap = np.random.poisson(bgMap)

        # Calculate relative intensity
        relInt = (dummyMap/bgMap - 1)
        relInt[relInt != relInt] = 0    # deal with NaN's

        # Weight, shift, calculate power spectrum
        relint_w = relInt * weight
        relint_w -= np.average(relint_w)
        fakeCl[n] = hp.anafast(relint_w)
        

    # Calculate 1-, 2-, and 3-sigma containment values from simulated Cls
    lims = [0.15, 2.5, 16, 84, 97.5, 99.85]
    fCl = np.percentile(fakeCl, lims, axis=0)

    # Remove monopole (l=0)
    fCl = fCl[:,1:]

    iso = {}
    vals = [-3, -2, -1, 1, 2, 3]
    for i, val in enumerate(vals):
        iso[val] = fCl[i]

    # Save as dictionary
    np.save(f'{args.out}.npy', iso)
    print(f'Isotropic noise bands are saved to {args.out}.npy')




