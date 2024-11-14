#!/usr/bin/env python

import numpy as np

#from icecube.photospline import spglam as glam
from icecube.photospline.glam import glam
from icecube.photospline import splinefitstable

#import photospline 
#from photospline import glam_fit, ndsparse, bspline

##============================================================================
## Functions for finding percentile, variance, and median of a histogram

def histPercentile(h, p, binMids):
    tot = h.sum()
    if tot == 0:
        return 0
    p_idx = np.where(h.cumsum()/tot > p/100)[0][0]
    return binMids[p_idx]


def histVar(h, binMids):
    if h.sum() == 0:
        return 0
    vals = np.asarray(binMids)
    ave = np.average(vals, weights=h)
    var = np.average((vals-ave)**2, weights=h)
    return var


def histMedian(h, bins):

    # Assume you only want to operate on the last dimension
    nx, ny, nz = h.shape
    median, sigL, sigR, var = np.zeros((4,nx,ny))
    emids = (bins[-1][:-1] + bins[-1][1:]) / 2
    for i in range(nx):
        for j in range(ny):
            median[i][j] = histPercentile(h[i][j], 50, emids)
            sigL[i][j]   = histPercentile(h[i][j], 16, emids)
            sigR[i][j]   = histPercentile(h[i][j], 84, emids)
            var[i][j]    = histVar(h[i][j], emids)

    return median, sigL, sigR, var


##============================================================================
## Return the median, +/-34% containment, and variance for each energy bin

def ebin_params(inFile, ebins, spline=True, validation=False):

    # Load simulation stored as numpy histogram + bins
    if validation:
        inFile = inFile.replace('_hist.npy', '_train.npy')
    d = np.load(inFile, allow_pickle=True)
    d = d.item()
    h, bins = d['hist'], d['bins']

    # Storage for output parameters
    median, sigL, sigR, var = np.zeros((4, len(ebins)-1))

    # Calculate spline energy values for bins
    if spline:
        splineFile = inFile.replace('.npy', '_spline.fits')
        xmids = (bins[0][1:] + bins[0][:-1])/2
        ymids = (bins[1][1:] + bins[1][:-1])/2
        tab = splinefitstable.read(splineFile)
        fit = glam.grideval(tab, [xmids, ymids])
        #tab = photospline.SplineTable(splineFile)
        #fit = tab.grideval([xmids, ymids])
    else:
        fit = histMedian(h, bins)[0]

    # Need to separately load testing histogram if validating
    if validation:
        inFile = inFile.replace('train','test')
        d = np.load(inFile, allow_pickle=True)
        d = d.item()
        h, bins = d['hist'], d['bins']

    # Evaluate parameters for each energy range
    zmids = (bins[2][1:] + bins[2][:-1])/2
    for i in range(len(ebins)-1):
        emin, emax = ebins[i:i+2]
        h_i = h[(fit > emin) & (fit < emax)].sum(axis=0)
        median[i] = histPercentile(h_i, 50, zmids)
        sigL[i]   = histPercentile(h_i, 16, zmids)
        sigR[i]   = histPercentile(h_i, 84, zmids)
        var[i]    = histVar(h_i, zmids)

    return median, sigL, sigR, var


    
