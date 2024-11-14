#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py3-v4.1.1/icetray-start
#METAPROJECT icetray/stable

import os,sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import argparse

import matplotlib.colors as colors
import matplotlib.cm as cmx

#from icecube.photospline import spglam as glam
from icecube.photospline.glam import glam
from icecube.photospline import splinefitstable

#import photospline 
#from photospline import glam_fit, ndsparse, bspline

from mapFunctions.histFunctions import histMedian, histPercentile, ebin_params

# Import standard output paths from directories.py in parent directory
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from mapFunctions import directories as ani

def getEbins():
    return [4, 4.25, 4.5, 4.75, 5, 5.25, 5.5, 6, 6.5]


def medianEnergy(emin, emax):

    # Establish path to analysis simulation location
    ani.setup_input_dirs(verbose=False)

    # Syntax is a little confused - was written to work with many ebins
    medians, sigL, sigR, var = ebin_params(ani.sim_hist, [emin, emax])
    medians = 10**(medians+9)
    labels = []
    for m in medians:
        # Fun syntax rounds to two sig figs
        if m >= 1e15:
            labels += [f'{float(f"{m/1e15:.2g}"):g} PeV']
        elif m >= 1e12:
            labels += [f'{float(f"{m/1e12:.2g}"):g} TeV']

    return labels[0]


def cmap_discretize(cmap, bins):

    bins = np.array(bins)
    N = len(bins) - 1
    colors_i = np.concatenate((np.linspace(0, 1., N), (0.,0.,0.,0.)))
    colors_rgba = cmap(colors_i)
    diffs = bins[1:] - bins[:-1]
    diffs /= diffs.sum()
    indices = np.zeros(len(bins))
    for i, diff in enumerate(diffs):
        indices[i+1] = indices[i] + diff
    indices[-1] = 1
    cdict = {}
    for ki, key in enumerate(('red','green','blue')):
        cdict[key] = [(indices[i], colors_rgba[i-1,ki], colors_rgba[i,ki]) \
                for i in range(N+1)]
    return matplotlib.colors.LinearSegmentedColormap('Custom', cdict, 1024)


""" Show the histogram used for reconstructing energy """
def reco_energy_plot(inFile, outFile, spline=False):

    # Load binned simulation
    d = np.load(inFile, allow_pickle=True)
    d = d.item()
    h, bins = d['hist'], d['bins']

    xbins, ybins, zbins = bins
    ebins = getEbins() + [8]

    # Calculate spline / median energy values
    energies, sigL, sigR, var = histMedian(h, bins)
    if spline:
        splineFile = inFile.replace('.npy', '_spline.fits')
        tab = splinefitstable.read(splineFile)
        energies = glam.grideval(tab, [xbins, ybins])
        #tab = photospline.SplineTable(splineFile)
        #energies = tab.grideval([xbins, ybins])

    # Additional options
    energies[energies==0] = energies.max()      # 0 events only at high E
    #  - finer binning for x & y if using splines?
    #  - cmap.set_under('white')

    # Plot formatting
    #fig, ax = plt.subplots(figsize=(10,8))
    fig, ax = plt.subplots(figsize=(5,4))
    matplotlib.rc("font", family="serif")
    tPars = {'fontsize':16}
    cmap = plt.cm.jet
    cmap = cmap_discretize(cmap, ebins)
    cmap.set_under('white')

    # Plot
    X, Y = np.meshgrid(xbins, ybins)
    p = ax.pcolor(X, Y, energies.T, cmap=cmap, vmin=ebins[0], vmax=ebins[-1])
    cb = fig.colorbar(p, ax=ax, ticks=ebins)
    cb.ax.set_yticklabels(['%.2f' % ebin for ebin in ebins])
    cb.set_label(r'$\mathrm{log}_{10}(E/\mathrm{GeV})$',
            rotation=270, labelpad=20, **tPars)
    ax.set_xlabel(r'$\mathrm{cos}(\theta_\mathrm{reco})$', **tPars)
    ax.set_ylabel(r'$\mathrm{log}_{10}(N_\mathrm{channel})$', **tPars)
    ax.set_xlim(xbins.min(), xbins.max())
    ax.set_ylim(ybins.min(), ybins.max())

    plt.savefig(outFile, dpi=300, bbox_inches='tight')


""" True energy distribution of reconstructed energy bins """
def ebin_dist(inFile, outFile, ebins, nomids=False):

    # Basic setup
    fig, ax = plt.subplots(figsize=(6,4.8))
    d = np.load(inFile, allow_pickle=True)
    d = d.item()
    h, bins = d['hist'], d['bins']

    # Calculate spline energy values for bins
    splineFile = inFile.replace('.npy', '_spline.fits')
    xmids = (bins[0][1:] + bins[0][:-1])/2
    ymids = (bins[1][1:] + bins[1][:-1])/2
    tab = splinefitstable.read(splineFile)
    fit = glam.grideval(tab, [xmids, ymids])
    #tab = photospline.SplineTable(splineFile)
    #fit = tab.grideval([xmids, ymids])

    jet = cm = plt.get_cmap('jet') 
    modEbins = getEbins() + [8]
    jet = cmap_discretize(jet, modEbins)
    cNorm  = colors.Normalize(vmin=modEbins[0], vmax=modEbins[-1])
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
    

    # Evaluate parameters for each energy range
    zmids = (bins[2][1:] + bins[2][:-1])/2
    for i in range(len(ebins)-1):

        if nomids:
            if i!=0 and i!=len(ebins)-2:
                continue

        emin, emax = ebins[i:i+2]
        h_i = h[(fit > emin) & (fit < emax)].sum(axis=0)

        emed = (modEbins[i] + modEbins[i+1])/2
        colorVal = scalarMap.to_rgba(emed)
        colorText = (
            'color: (%4.2f,%4.2f,%4.2f)'%(colorVal[0],colorVal[1],colorVal[2])
        )
        label = medianEnergy(emin, emax)
        #label = label.replace('.0', '') # remove trailing zeroes
        ax.step(zmids, h_i/h_i.sum(), label=label, color=colorVal)

    # Additional plot work
    ax.set_xlim(2.75, 8.5)
    tPars = {'fontsize':16}
    ax.set_xlabel(r'True Energy ($\log_{10}(E/\mathrm{GeV})$)', **tPars)
    ax.set_ylabel('Fraction of Events', **tPars)
    ax.legend()
    # Custom text labels
    #ax.text(0.2, 0.62, '1', transform=ax.transAxes)

    plt.savefig(outFile, dpi=300, bbox_inches='tight')


""" Testing energy distribution of reconstructed energy bins, using split
training and testing histograms """
def ebin_dist_validation(trainFile, testFile, outFile, ebins):

    # Basic setup
    fig, ax = plt.subplots()
    d = np.load(trainFile, allow_pickle=True)
    d = d.item()
    h_train, bins = d['hist'], d['bins']
    d = np.load(testFile, allow_pickle=True)
    d = d.item()
    h_test, bins = d['hist'], d['bins']

    # Calculate spline energy values for bins
    splineFile = trainFile.replace('.npy', '_spline.fits')
    xmids = (bins[0][1:] + bins[0][:-1])/2
    ymids = (bins[1][1:] + bins[1][:-1])/2
    tab = splinefitstable.read(splineFile)
    fit = glam.grideval(tab, [xmids, ymids])
    #tab = photospline.SplineTable(splineFile)
    #fit = tab.grideval([xmids, ymids])

    # Calculate median energy values for bins
    median, sigL, sigR, var = histMedian(h_train, bins)

    # Plot energy distribution for each energy range
    zmids = (bins[2][1:] + bins[2][:-1])/2
    for i in range(len(ebins)-1):
        emin, emax = ebins[i:i+2]
        # For splined values
        h_i = h_test[(fit > emin) & (fit < emax)].sum(axis=0)
        ax.step(zmids, h_i/h_i.sum(), label=i+1, color='blue')
        # For histogrammed values
        h_i = h_test[(median > emin) & (median < emax)].sum(axis=0)
        ax.step(zmids, h_i/h_i.sum(), label=i+1, color='red')

    # Additional plot work
    ax.set_xlim(2.75, 8.5)
    tPars = {'fontsize':16}
    ax.set_xlabel(r'True Energy ($\log_{10}(E/\mathrm{GeV})$)', **tPars)
    ax.set_ylabel('Fraction of Events', **tPars)
    # Custom text labels
    #ax.text(0.2, 0.62, '1', transform=ax.transAxes)

    plt.savefig(outFile, dpi=300, bbox_inches='tight')


""" Simplified visualization of energy distributions """
def ebin_width(inFile, outFile, ebins, validation=False):

    # Basic setup
    fig, ax = plt.subplots()
    emids = (np.asarray(ebins)[1:] + np.asarray(ebins)[:-1])/2
    emids[-1] = (8+6.5)/2   # Custom setup for highest energy bin

    # Summary parameters for smoothed energy bins
    median, sigL, sigR, var = ebin_params(inFile, ebins, validation=validation)
    ax.errorbar(emids, median, yerr=(median-sigL, sigR-median), fmt='.',
            color='blue', capsize=4, label='Splined')

    if validation:    

        # Summary parameters for unsmoothed energy bins
        median, sigL, sigR, var = ebin_params(inFile, ebins, 
                spline=False, validation=validation)
        ax.errorbar(emids, median, yerr=(median-sigL, sigR-median), fmt='.',
                color='red', capsize=4, label='Unsmoothed')

    # Additional plot work
    ax.set_xlim(2.75, 8.5)
    tPars = {'fontsize':16}
    ax.set_xlabel(r'Energy of Bin Center ($\log_{10}(E/\mathrm{GeV})$)', 
            **tPars)
    ax.set_ylabel(r'True Energy ($\log_{10}(E/\mathrm{GeV})$)', **tPars)

    if validation:
        plt.legend()

    plt.savefig(outFile, dpi=300, bbox_inches='tight')


""" Overlap in true energy distribution of reconstructed energy bins """
def overlap(inFile, ebins):

    # Basic setup
    d = np.load(inFile, allow_pickle=True)
    d = d.item()
    h, bins = d['hist'], d['bins']

    # Calculate spline energy values for bins
    splineFile = inFile.replace('.npy', '_spline.fits')
    xmids = (bins[0][1:] + bins[0][:-1])/2
    ymids = (bins[1][1:] + bins[1][:-1])/2
    tab = splinefitstable.read(splineFile)
    fit = glam.grideval(tab, [xmids, ymids])

    # Evaluate parameters for each energy range
    emin1, emax1, emin2, emax2 = ebins
    pdf1 = h[(fit > emin1) & (fit < emax1)].sum(axis=0)
    pdf1 /= pdf1.sum()
    cdf1 = np.cumsum(pdf1)
    pdf2 = h[(fit > emin2) & (fit < emax2)].sum(axis=0)
    pdf2 /= pdf2.sum()
    cdf2 = np.cumsum(pdf2)

    crossover = np.where(cdf2 >= 1-cdf1)[0][0]
    overlap_prob = np.sum(pdf1[crossover:]) + np.sum(pdf2[:crossover])
    print(f'Overlap for {emin1}-{emax1} vs {emin2}-{emax2} : {overlap_prob * 100:.02f}%')


if __name__ == "__main__":

    # Establish paths to analysis simulation location
    ani.setup_input_dirs(verbose=False)

    p = argparse.ArgumentParser(
            description='Simulation plots for in-ice DST simulation')

    # General
    p.add_argument('-i', '--inFile', dest='inFile',
            default=ani.sim_hist,
            help='Input simulation file stored as numpy histogram + bins')
    p.add_argument('--trainFile', dest='trainFile',
            default=ani.sim_hist.replace('_hist','_train'),
            help='Input simulation file stored as numpy histogram + bins')
    p.add_argument('--testFile', dest='testFile',
            default=ani.sim_hist.replace('_hist','_test'),
            help='Input simulation file stored as numpy histogram + bins')
    p.add_argument('-o', '--outFile', dest='outFile',
            help='Output file destination')

    # Rainbow plot
    p.add_argument('--rainbow', dest='rainbow',
            default=False, action='store_true',
            help='Produce the reconstructed energy (rainbow) plot')
    p.add_argument('--spline', dest='spline',
            default=False, action='store_true',
            help='Use splined energies for rainbow plot')

    # Energy distribution for energy bins
    p.add_argument('--edist', dest='edist',
            default=False, action='store_true',
            help='True energy distribution split by reco energy bin')
    p.add_argument('--validation', dest='validation',
            default=False, action='store_true',
            help='Apply validation check to energy distributions')
    # Summary view for above
    p.add_argument('--ewidth', dest='ewidth',
            default=False, action='store_true',
            help='Energy distribution for energy bins (summary view)')
    p.add_argument('--ebins', dest='ebins', nargs='+',
            default=getEbins() + [100], type=float,
            help='Use custom reconstructed energy binning')
    p.add_argument('--nomids', dest='nomids',
            default=False, action='store_true',
            help='Omit middle energy bins for energy distribution plot')

    p.add_argument('--overlap', dest='overlap',
            default=False, action='store_true',
            help='')

    args = p.parse_args()

    if args.rainbow:
        reco_energy_plot(args.inFile, args.outFile, args.spline)
        quit()      # Running multiple plots is illegal (only one output name)

    if args.edist:
        if args.validation:
            ebin_dist_validation(args.trainFile, args.testFile, 
                                 args.outFile, args.ebins)
        else:
            ebin_dist(args.inFile, args.outFile, args.ebins, args.nomids)
        quit()

    if args.ewidth:
        ebin_width(args.inFile, args.outFile, args.ebins, args.validation)

    if args.overlap:
        overlap(args.inFile, [4,4.25, 5.5,100])




