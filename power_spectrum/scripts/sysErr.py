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

from map_functions import getMap

if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Makes angular power spectrum error bars.',
            epilog='To run: python [code] -f [path to input file] -o [path to output file]. -n can be set to any integer and is defaulted to 1e5')
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

        # Load relative intensity (unsmoothed by default)
        relint = getMap(args.files, mapName='relint', mask=True, multi=multi,
                smooth=args.smooth, norm=norm)

        # Background map used for weighting
        bgMap = getMap(args.files, mapName='bg', mask=True, 
                smooth=args.smooth, norm=norm)
        bgMap[bgMap==hp.UNSEEN] = 0
        # "Normalize" by dividing by average value of unmasked pixels
        bgMap /= bgMap[bgMap != 0].mean()

        # Apply weight and shift to keep average relative intensity at 0
        relint_w = relint * bgMap
        relint_w -= np.average(relint_w)

        # Map parameters (should be the same for both maps)
        npix = relint.size
        nside = hp.npix2nside(npix)
        lmax = 3*nside - 1

        # Calculate power spectrum
        y = hp.anafast(relint_w, lmax=lmax)

        # Generate fake maps, calculate power spectra, and store
        fakeCl = np.zeros((args.n, lmax+1))
        for n in range(args.n):
            fakeRL = hp.synfast(y, nside=nside, verbose=False)
            # Calculate and store power spectrum
            fakeCl[n] = hp.anafast(fakeRL, lmax=lmax)

        # Calculate 1-sigma containment values from simulated Cls
        lims = [16, 84]
        fCl = np.percentile(fakeCl, lims, axis=0)

        # Convert 1-sigma containments to errorbar format for plotting
        dCl = [ y-fCl[0], fCl[1]-y ]

        # Save to text file
        out = f'{args.out}'
        if multi != False:
            out += f'_m{multi}'
        np.savetxt(f'{out}.txt', dCl)
        print(f'Systematic errorbars written to {out}.txt')





