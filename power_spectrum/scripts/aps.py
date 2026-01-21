#!/usr/bin/env python
# coding: utf-8

import argparse
import healpy as hp
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
import scipy
import numpy as np

import os, sys

# Import standard analysis paths from directories.py in parent directory
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

# import packages from hpenv virtual environment
#sys.path.append('/home/ahinners/hpenv/lib/python3.12/site-packages')

if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Creates angular power spectra.',
            epilog='To run: python [code] -f [intput file path] -i [iso error path] --staterr [stat error path] --syserr [sys error path] -o [output file path]')
            
    p.add_argument('-f', '--files', dest='files',
            nargs='+', action='append',
            help='Input filenames. Use -f flag for each set of files.')
    p.add_argument('-o', '--out', dest='out',
            help='Output image filename.')
    p.add_argument('-l', '--label', dest='label',
            nargs = '+',
            help ='Labels for plot legend')
    p.add_argument('-sy', '--syserr', dest='syserr',
            nargs='+', action ='append',
            help ='Input error bar files from sysErr.py')
    p.add_argument('-st', '--staterr', dest='staterr',
            nargs='+', action ='append',
            help ='Input error bar files from statErr.py')
    p.add_argument('-m', '--multi', dest='multi',
            default=False, action='store_true',
            help='Set to also show data w/ ell=2 multipole subtraction')
    p.add_argument('-s', '--smooth', dest='smooth',
            type=float, default=0,
            help='Smooth data and background maps')
    p.add_argument('-i', '--iso', dest='iso',
            nargs = '+',
            help ='Input isotropic noise band files from isoErr.py')
    p.add_argument('-il', '--iso_labels', dest='iso_labels',
            default=False, action='store_true',
            help='Suppress the output of noise labels in legend')
    p.add_argument('-icp', '--ice_prelim', dest='icp',
                   default=False, action ='store_true',
                   help='Adds IceCube Preliminary to power spectrum')
    p.add_argument('--fit-2d', dest='fit2d',
        default=False, action='store_true',
        help='Use 2d fit for l=1,2,3 instead of 1D projection')
    

    args = p.parse_args()

#else: 
    #Avoid boosted counts if top-hat smoothing applied
    norm = True if args.smooth!=0 else False

    # Plot setup
    fig = plt.figure(1, figsize=(7.5,3.75))
    ax = fig.add_subplot(111)
    fig.patch.set_facecolor('white')

    # Axis setup and labels
    xlim=40
    tparams = {'fontsize':14}
    ax.set_yscale('log')
    ax.set_xlim([0, xlim])
    ax.set_ylim([10**-12, 10**-5])
    ax.set_xlabel(r"multipole $\ell$", **tparams)
    ax.set_ylabel(r'$\tilde{C}_{\ell}$', **tparams)
    ax.tick_params(axis='both', which='major', labelsize=14, length=10)
    ax.grid(False)  # Hide gridlines

    # Labels for upper x-axis (in degrees)
    a2 = ax.twiny()
    ticks = [1., 4., 9., 18., 36., xlim]
    deg = lambda cl: [(r"%g$^\circ$" % (180./c)) for c in cl]
    a2.set_xticks(ticks)
    tick_labels = deg(ticks)
    tick_labels[-1]=""
    a2.set_xticklabels(tick_labels, **tparams)

    # Series formatting
    fmt = {'marker':'o', 'linestyle':'none'}
    multipoles = [False] if not args.multi else [False, 2]
    # Systematic error bar setup
    eb = {'edgecolor':None, 'linewidth':0, 'linestyle':None}

    for i, f in enumerate(args.files):

        # Calculate for maps with/out multipole fit subtraction
        for j, multi in enumerate(multipoles):

            # Load relative intensity (unsmoothed by default)
            relint = getMap(f, mapName='relint', mask=True, multi=multi,
                    smooth=args.smooth, norm=norm)

            # Map paramaters
            npix = relint.size
            nside = hp.npix2nside(npix)
            lmax = 3*nside - 1

            # Background map used for weighting
            bgMap = getMap(f, mapName='bg', mask=True,
                    smooth=args.smooth, norm=norm)
            bgMap[bgMap == hp.UNSEEN] = 0
            # "Normalize" by dividing by average value of unmasked pixels
            bgMap /= bgMap[bgMap != 0].mean()

            # Apply weight and shift to keep average relative intensity at 0
            relint_w = relint * bgMap
            relint_w -= np.average(relint_w)

            # Calculate power spectrum
            y = hp.anafast(relint_w, lmax=lmax)
            x = np.arange(len(y))

            # Labeling
            label = ' '.join(args.label[i].split('_')).replace('[','').replace(']','').replace("'","")
            if multi != False:
                label += ' (small-scale)'

            # Systematic error bars if available (generated with sysErr)
            dc = '#FF4242' # dc for dot (and error bar) color 
            if args.staterr:
                dCl = np.loadtxt(args.staterr[i][j])
                l = ax.errorbar(x, y, yerr=dCl, label=label, **fmt, c=dc, ecolor = '#363636', markeredgecolor='#363636')
            else:
                l = ax.plot(x, y, label=label, **fmt)

            if args.syserr:
                dCl = np.loadtxt(args.syserr[i][j])
                box = 0.8
                patches = [mpl.patches.Rectangle([x[k]-box/2, y[k]-dCl[0][k]],
                        box, dCl[0][k]+dCl[1][k], **eb) for k in range(len(x))]
                cln = PatchCollection(patches, cmap=mpl.cm.jet,
                        alpha=0.5, facecolor=l[0].get_color())
                ax.add_collection(cln)

        # Plot isotropic noise bands (generated with isoErr)
        if args.iso:
            iso = np.load(args.iso[i], allow_pickle=True)
            iso = iso.item()
            handles, labels = ax.get_legend_handles_labels()
            # Colors reverse sorted so the narrower bands lay on top
            c = {3:'#7C98B3', 2:'#ACCBE1', 1:'#CEE5F2'}
            for k, color in c.items():
                ax.fill_between(x[1:], iso[-k], iso[k], lw=0, color=color,
                        zorder=0)   # draw behind systematic errors
            # Then sort entries so they're listed as expected in the legend
            if args.iso_labels:
                for k, color in sorted(c.items()):
                    handles += [mpl.patches.Patch(color=color, 
                                label=fr'noise (${k}\sigma$)')]

    # Finish and save
    fig.legend(handles=handles, fontsize='large', bbox_to_anchor=(.96,.895))
    fig.tight_layout()
    if args.icp:
        plt.text(10, 1e-7, 'IceCube Preliminary', color='black', fontsize = 20)
    
    print(f'Writing file to {args.out}')
    plt.savefig(args.out)



