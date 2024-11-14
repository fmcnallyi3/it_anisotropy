#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py3-v4.1.1/icetray-start
#METAPROJECT icetray/stable

import healpy as hp
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
#from tabulate import tabulate
import glob, argparse, os, sys

# Import standard analysis paths from directories.py in parent directory
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from icesim.histFunctions import ebin_params
from mapFunctions.map_functions import getMap
from mapFunctions.proj1d import getRelInt
import directories as ani

def getEbins():
    return [4, 4.25, 4.5, 4.75, 5, 5.25, 5.5, 6, 6.5, 100]


def cosinefit(x, *p):
    k = 2*np.pi / 360       # Wavenumber (assumes x in degrees)
    l = len(p) // 2         # Multipole number of fit
    return sum([p[2*i] * np.cos((i+1)*k*x - p[2*i+1]) for i in range(l)])


def multipoleFit(x, y, l, sigmay, fittype='cos'):

    # Guess at best fit parameters
    amplitude = (3./np.sqrt(2)) * np.std(y)
    phase     = 0
    p0 = [amplitude, phase] * l
    # Reduce amplitude as we go to higher l values
    for i in range(0, len(p0)//2):
        p0[2*i] *= 2.**(-i)

    # Do best fit
    popt, pcov = curve_fit(cosinefit, x, y, p0, sigma=sigmay)
    fitVals = cosinefit(x, *popt)
    ndof  = len(popt)
    reduced_chi2 = (1. / (len(y)-ndof)) * sum((y - fitVals)**2 / sigmay**2)
    perr = np.sqrt(np.diag(pcov))
    #perr = perr_scaled / chi2

    return popt, perr, reduced_chi2


if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='')
    p.add_argument('-f', '--files', dest='files',
            default='energy',
            choices=['energy','config','comp','solar'],
            help='Choose from presets for files to run over')
    p.add_argument('--chi2', dest='chi2',
            default=False, action='store_true',
            help='Show chi2 for a variety of "multipole" fits')
    p.add_argument('-l', '--lvalue', dest='l', type=int,
            help="Option to fix l-value for multipole fit")
    p.add_argument('-n', '--nbins', dest='nbins', 
            type=int, default=24,
            help='Number of bins for the 1D fit')
    p.add_argument('--solo', dest='solo', type=int,
            help="Option to plot an individual file's sine fits")
    p.add_argument('--offset', dest='offset', type=int,
            help='Shift phase by some offset value')
    p.add_argument('-o', '--out', dest='out',
            default=None,
            help="Option to write to file")
    p.add_argument('-S', '--scale', dest='scale',
            type=int, default=0,
            help='Exponential scale for multiplying y-axis')
    p.add_argument('--weight_RI', dest='weight_RI',
            default=False, action='store_true',
            help='Use unweighted average for 1D projection')
    args = p.parse_args()

    # Establish standard paths to analysis data
    ani.setup_input_dirs(verbose=False)
    
    if args.files == 'config':
        files = glob.glob(f'{ani.maps}/IC86-*_24H_sid.fits')
        configs = np.array([os.path.basename(f).split('_')[0] for f in files])
        csort = configs.argsort()
        configs, files = configs[csort], np.asarray(files)[csort]
        x = range(len(configs))
        smooth = 5

    if args.files == 'energy':
        files = sorted(glob.glob(f'{ani.maps}/IC86_24H_*GeV*'))
        ebins = getEbins()
        x, xL, xR, _ = ebin_params(ani.sim_hist, ebins)
        xL = x - xL
        xR = xR - x
        smooth = 20

    if args.files == 'solar':
        files = glob.glob(f'{ani.maps}/IC86_24H_solar.fits')
        smooth = 5
        x = ['solar']

    if args.solo == 0:
        fig = plt.figure(figsize=(8,6))
        ax = fig.add_subplot(111)

    nfiles = len(files)
    lmax = args.nbins/2 - 1
    if lmax > 15:
        lmax = 15

    # Y-axis scale
    scale = 10**args.scale

    opts = {'mask':True, 'ramin':0., 'ramax':360., 'nbins':args.nbins}
    opts['weight_RI'] = args.weight_RI
    amp, phase, amp_err, phase_err = np.zeros((4, nfiles))
    chi2array = np.zeros((nfiles,lmax-1))

    # Calculate best multipole-fit value based on chi2
    for i, f in enumerate(files):
        ra, ri, sigmax, sigmay = getRelInt(f, **opts)
        ri *= scale
        sigmay *= scale
        for l in range(1, lmax):
            popt, perr, chi2 = multipoleFit(ra, ri, l, sigmay)
            chi2array[i][l-1] = chi2
            if i == args.solo:
                ax.errorbar(ra, ri, sigmay, fmt='.')
                fullra = range(360)
                fit = [cosinefit(j, *popt) for j in fullra]
                ax.plot(fullra, fit, label=l)

    if args.chi2:
        chi2table = chi2array.tolist()
        chi2table = [[x[i]] + chi2 for i, chi2 in enumerate(chi2table)]
        print('Temporarily broken (ImportError: bad magic number in tabulate)')
        #print(tabulate(chi2table, headers=range(1,lmax), floatfmt='.2f'))

    if not args.l:
        chi2array[chi2array < .7] = 100
        args.l = chi2array.sum(axis=0).argmin() + 1

    for i, f in enumerate(files):
        ra, ri, sigmax, sigmay = getRelInt(f, **opts)
        ri *= scale
        sigmay *= scale
        popt, perr, chi2 = multipoleFit(ra, ri, args.l, sigmay)
        a = np.reshape(popt, (-1,2))
        amp[i], phase[i] = a[0]
        e = np.reshape(perr, (-1,2))
        amp_err[i], phase_err[i] = e[0]

    phase *= 180/np.pi
    phase_err *= 180/np.pi

    # Deal with negative amplitudes/phases
    c0 = amp < 0
    amp[c0] *= -1.
    phase[c0] += 180
    phase[phase > 360] -= 360
    phase[phase < 0] += 360

    # Formatting for plot points
    pltParams = {'fmt':'.', 'lw':2, 'ms':14}

    if args.solo == None:

        fig = plt.figure(figsize=(25,6))
        ax = fig.add_subplot(121)
        #ax.set_title('Amplitude', fontsize=16)
        ax.set_xlabel(r'$\mathrm{log}_{10}(E/\mathrm{GeV})$', fontsize=14)
        ylabel = r'$\Delta N/\langle N \rangle$'
        if args.scale != 0:
            ylabel += fr'$\; (\times 10^{{{-args.scale}}})$'
        ax.set_ylabel(ylabel, fontsize=14)
        if args.files == 'config':
            ax.set_xlim(-1, x[-1]+1)
            ax.set_xticks(x)
            ax.set_xticklabels(configs)
            ax.set_xlabel('Detector Configuration')
        if args.files == 'comp':
            ax.set_xlabel('Energy per Nucleon')
            ax.set_xlim(0, 1.1)

        if args.files == 'energy':
            ax.errorbar(x, amp, xerr=[xL,xR], yerr=amp_err, c='b', **pltParams)
            ax.set_ylim(0, 0.002*scale)
        else:
            ax.errorbar(x, phase, yerr=phase_err, **pltParams)

        if args.offset != None:
            if args.files == 'energy':
                pcut = phase > args.offset - 20
                phase[pcut] -= args.offset
                phase[np.logical_not(pcut)] += (360 - args.offset)
            else:
                pcut = phase > args.offset
                phase[pcut] -= args.offset
                phase[np.logical_not(pcut)] += (360 - args.offset)

        ax = fig.add_subplot(122)
        #ax.set_title('Phase', fontsize=16)
        ax.set_xlabel(r'$\mathrm{log}_{10}(E/\mathrm{GeV})$', fontsize=14)
        #ax.set_ylabel(r'Dipole phase $(\phi/\mathrm{deg})$', fontsize=14)
        ax.set_ylabel(r'Right Ascension $[^{\circ}]$', fontsize=14)
        if args.files == 'config':
            ax.set_xlim(-1, x[-1]+1)
            ax.set_xticks(x)
            ax.set_xticklabels(configs)
            ax.set_xlabel('Detector Configuration')
        if args.files == 'comp':
            ax.set_xlabel('Energy per Nucleon')
            ax.set_xlim(0, 1.1)
        if args.files == 'energy':
            ax.errorbar(x, phase, xerr=[xL,xR], yerr=phase_err, 
                    c='b', **pltParams)
        else:
            ax.errorbar(x, phase, yerr=phase_err, **pltParams)
        ax.set_ylim(0,360)

    else:
        ax.legend(loc='lower right')

    if args.offset != None:
        ax.set_ylim(-25, 370)
        ax.set_yticks(range(0, 361, 45))
        ylabels  = [str(i) for i in range(args.offset, 360-1, 45)]
        ylabels += [str(i) for i in range(0, args.offset+1, 45)]
        ax.set_yticklabels(ylabels)

    plt.savefig(args.out, dpi=300, bbox_inches='tight')






