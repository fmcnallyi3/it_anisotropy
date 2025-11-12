#!/usr/bin/env python

from __future__ import print_function

import healpy as hp
import numpy as np
import sys, os, glob, time
from numpy import sqrt, pi
import scipy.optimize as opt
import scipy.stats.distributions as sd

# Import standard output paths from directories.py in parent directory
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
# from mapFunctions import directories as ani

def maskMap(m, decmin, decmax):

    degree = pi / 180.
    npix  = len(m)
    nside = hp.npix2nside(npix)
    theta, phi = hp.pix2ang(nside, range(npix))

    thetaMin = (90 - decmin) * degree
    thetaMax = (90 - decmax) * degree
    thetaCut = (theta <= thetaMin) * (theta >= thetaMax)

    new_map = np.copy(m)
    new_map[np.logical_not(thetaCut)] = hp.UNSEEN

    return new_map

# Li Ma Significance
def LMSignificance(nData, nBG, alpha, nData_wsq=None, nBG_wsq=None):

    with np.errstate(invalid='ignore', divide='ignore'):

        # Allow for scaling term if weighted square maps necessary
        scale = 1.
        if (nData_wsq != None) or (nBG_wsq != None):
            scale = (nData + nBG/alpha) / (nData_wsq + nBG_wsq/alpha)
        Non  = nData * scale
        Noff = nBG/alpha * scale

        sn = np.sign(nData - nBG)
        sigma = sn * sqrt(2*(Non*np.log(((1+alpha)*Non) / (alpha*(Non+Noff)))
            + Noff * np.log(((1+alpha)*Noff) / (Non+Noff))))

    return sigma

# Return the real Cartesian spherical harmonic for a given l, m
def norm_sphharm(l, m, vx, vy, vz):

    if l==0 and m==0:
        return 1/2. * sqrt(1/pi)
    if l==1 and m==-1:
        return vy * sqrt(3/(4*pi))
    if l==1 and m==0:
        return vz * sqrt(3/(4*pi))
    if l==1 and m==1:
        return vx * sqrt(3/(4*pi))
    if l==2 and m==-2:
        return vx*vy * 1/2. * sqrt(15/pi)
    if l==2 and m==-1:
        return vy*vz * 1/2. * sqrt(15/pi)
    if l==2 and m==0:
        return (3*vz**2 - 1.) * 1/4. * sqrt(5/pi)
    if l==2 and m==1:
        return vx*vz * 1/2. * sqrt(15/pi)
    if l==2 and m==2:
        return (vx**2 - vy**2) * 1/4. * sqrt(15/pi)
    if l==3 and m==-3:
        return (3*vx**2 - vy*vx) * vy * 1/4. * sqrt(35/(2*pi))
    if l==3 and m==-2:
        return vx*vy*vz * 1/2. * sqrt(105/pi)
    if l==3 and m==-1:
        return (5*vz**2 - 1) * vy * 1/4. * sqrt(21/(2*pi))
    if l==3 and m==0:
        return (vz**2 - 1) * vz * 1/4. * sqrt(7/pi)
    if l==3 and m==1:
        return (5*vz**2 - 1) * vx * 1/4. * sqrt(21/(2*pi))
    if l==3 and m==2:
        return (vx**2 - vy**2) * vz * 1/4. * sqrt(105/pi)
    if l==3 and m==3:
        return (vx**2 - 3*vy**2) * vx * 1/4. * sqrt(35/(2*pi))
    raise

# Return the real Cartesian spherical harmonic for a given l, m
def real_sphharm(l, m, vx, vy, vz):

    if l==0 and m==0:
        return 1.
    if l==1 and m==-1:
        return vy
    if l==1 and m==0:
        return vz
    if l==1 and m==1:
        return vx
    if l==2 and m==-2:
        return 2*vx*vy
    if l==2 and m==-1:
        return 2*vy*vz
    if l==2 and m==0:
        return sqrt(1/3.)*(3*vz**2 - 1.)
    if l==2 and m==1:
        return 2*vx*vz
    if l==2 and m==2:
        return (vx**2 - vy**2)
    if l==3 and m==-3:
        return (3*vx**2 - vy*vx) * vy
    if l==3 and m==-2:
        return sqrt(8/3.)*vx*vy*vz
    if l==3 and m==-1:
        return sqrt(3/5.)*(5*vz**2 - 1) * vy
    if l==3 and m==0:
        return sqrt(2/5.)*(vz**2 - 1) * vz
    if l==3 and m==1:
        return sqrt(3/5.)*(5*vz**2 - 1) * vx
    if l==3 and m==2:
        return sqrt(2/3.)*(vx**2 - vy**2) * vz
    if l==3 and m==3:
        return (vx**2 - 3*vy**2) * vx

## Creates dipole and quadrupole fit map
def multifit(l, data, bg, alpha=1/20., params=False, out=False,
             decmax=-25., decmin=-90., useROOT=False, **kwargs):

    # ROOT minimizer only required for comparison to 6-year analysis
    if useROOT:
        try: import ROOT
        except ImportError:
            print('ROOT minimizer desired but package not found. Exiting...')
            raise

    npix = len(data)
    nside = hp.npix2nside(npix)
    degree = pi / 180.
    minZ = decmin * degree
    maxZ = decmax * degree

    # Useful breakdown of l, m values to be used
    nsph = sum([2*l_i+1 for l_i in range(l+1)])
    lvals = [[l_i]*(2*l_i+1) for l_i in range(l+1)]
    mvals = [[m for m in range(-l_i, l_i+1)] for l_i in range(l+1)]
    lvals = [item for sublist in lvals for item in sublist]
    mvals = [item for sublist in mvals for item in sublist]

    # Calculate relative intensity and variance
    with np.errstate(invalid='ignore', divide='ignore'):
        skymap = (data - bg) / bg
        skymapVar = data * (bg + alpha*data) / (bg**3)
    skymap[np.isnan(skymap)] = 0
    skymapVar[np.isnan(skymapVar)] = np.inf

    # Restrict range to desired zenith angles
    vx, vy, vz = hp.pix2vec(nside, [i for i in range(npix)])
    zcut = (vz >= minZ) * (vz <= maxZ)
    skymap[np.logical_not(zcut)] = 0
    skymapVar[np.logical_not(zcut)] = np.inf
    ndata = zcut.sum()

    fitparams = ['Y(%i,%i)' % (lvals[i], mvals[i]) for i in range(nsph)]

    if useROOT:
        print('\nROOT requested and found: Using ROOT Minuit minimizer')
        def chi2(npar, derivatives, f, par, internal_flag):
            fit = np.zeros(len(vx))
            for i in range(len(lvals)):
                #fit += par[i] * real_sphharm(lvals[i], mvals[i], vx, vy, vz)
                fit += par[i] * norm_sphharm(lvals[i], mvals[i], vx, vy, vz)
            df = skymap - fit
            f[0] = (df**2 / skymapVar).sum()

        # Setup minimizer
        minimizer = ROOT.TMinuit(nsph)
        minimizer.SetFCN(chi2)
        error_code = ROOT.Long(0)
        minimizer.mnexcm("SET PRINTOUT", np.array([-1]), 1, error_code)
        for i, p in enumerate(fitparams):
            minimizer.mnparm(i, p, 0., 1e-6, -1e6, 1e6, error_code)

        # Iterate MIGRAD up to 1000 times
        minimizer.mnexcm("SET STR", np.array([2]), 1, error_code)
        minimizer.mnexcm("MIGRAD", np.array([1000]), 1, error_code)

    else:
        #print('\nUsing scipy L-BFGS-B minimizer')
        # Chi-squared function to minimize for fit
        def chi2(par):
            fit = np.zeros(len(vx))
            for i in range(len(lvals)):
                #fit += par[i] * real_sphharm(lvals[i], mvals[i], vx, vy, vz)
                fit += par[i] * norm_sphharm(lvals[i], mvals[i], vx, vy, vz)
            df = skymap - fit
            return (df**2 / skymapVar).sum()

        # Setup minimizer
        x0 = [0 for i in range(nsph)]
        minimizer = opt.minimize(chi2, x0, method='L-BFGS-B')

    # Extract best fit parameters
    p = getFitParams(minimizer, fitparams, ndata, useROOT)

    if params:
        return p

    # Create map with dipole/quadrupole fit
    fitmap = np.zeros(len(vx))
    for i in range(nsph):
        #fitmap += p[fitparams[i]] * real_sphharm(lvals[i],mvals[i],vx,vy,vz)
        fitmap += p[fitparams[i]] * norm_sphharm(lvals[i],mvals[i],vx,vy,vz)

    if out:
        hp.write_map(out, fitmap)
        return

    return fitmap


## Get dipole/quadrupole fit parameters in dictionary
def getFitParams(minimizer, fitparams, ndata, useROOT):

    p = {}

    if useROOT:
        import ROOT
        p['chi2'], edm, errdef = [ROOT.Double(0) for i in range(3)]
        nvpar, nparx, ierr = [ROOT.Long(0) for i in range(3)]
        minimizer.mnstat(p['chi2'], edm, errdef, nvpar, nparx, ierr)
        #p['chi2'] = amin
        p['ndof'] = ROOT.Long(ndata - nvpar)
        p['prob'] = ROOT.TMath.Prob(p['chi2'], p['ndof'])
        for i, par in enumerate(fitparams):
            p[par], p['d'+par] = ROOT.Double(0), ROOT.Double(0)
            minimizer.GetParameter(i, p[par], p['d'+par])

    else:
        p['chi2'] = minimizer.fun
        p['ndof'] = ndata - len(fitparams)
        #p['prob'] = chisqprob(p['chi2'], p['ndof'])
        p['prob'] = sd.chi2.sf(p['chi2'], p['ndof'])
        # Attempt at uncertainties
        # Adapted from stackoverflow.com/questions/43593592/errors-to-fit...
        ftol = 2.220446049250313e-09
        ## Line may fail if using outdated scipy!!
        cov = minimizer.hess_inv.todense()
        scaled_cov = cov * p['chi2'] / p['ndof']
        unc = np.sqrt(ftol * scaled_cov.diagonal())
        for i, par in enumerate(fitparams):
            p[par] = minimizer.x[i]
            p['d'+par] = unc[i]

    return p


## Ouput parameters from dipole/quadrupole fit
def outputFit(p, fitparams, scale):

    print('\nchi2/ndf = %.1f / %d = %.2e' % (p['chi2'], p['ndof'], p['prob']))
    print('Fit values (x %d):' % scale)
    for par in fitparams:
        print(' %s = %.3f +/- %.3f' % (par, scale*p[par], scale*p['d'+par]))


# Takes in data, bg & dipole-quadrupole maps and creates false data map
def multi_subtraction(l, data, bg, alpha=1/20., decmin=-25., decmax=-90.,
                      fix_multi=False,
                      fix_data=None, fix_bg=None, **kwargs):

    opts = locals()
    # Eliminate variables you don't want to pass to multifit (clumsy)
    for i in ['l','data','bg','kwargs']:
        opts.pop(i)

    # Create residual map
    with np.errstate(invalid='ignore'):
        relint = (data - bg) / bg
    relint[np.isnan(relint)] = 0.

    if fix_multi:
        fit = multifit(l, fix_data, fix_bg, **opts)
    else:
        fit = multifit(l, data, bg, **opts)
    residual = relint - fit

    # Create false data map and normalize
    new_data = bg * (residual + 1)
    norm = data.sum() / float(new_data.sum())
    new_data = new_data * norm

    return new_data


# "Top hat" smoothing over a given angle in degrees
def smoothMap(m, wtsqr=False, norm=False, **opts):

    if wtsqr==True:
        return None

    npix  = len(m)
    nside = hp.npix2nside(npix)
    smooth_rad = opts['smooth'] * pi/180.
    smooth_map = np.zeros(npix)

    vec = np.transpose(hp.pix2vec(nside, np.arange(npix)))
    for i in range(npix):
        neighbors = hp.query_disc(nside, vec[i], smooth_rad)
        smooth_map[i] += m[neighbors].sum()
        if norm:
            smooth_map[i] /= (len(neighbors) + 1)

    return smooth_map


# Takes a file consisting of data, bg, and local maps. Returns desired
# final type (relint, sig, etc) with smoothing, masking, and fitting options.
def getMap(inFiles, mapName=None, multi=False, smooth=0,
           swindow=3, mask=False, decmin=-90., decmax=90.,
           fix_multi=False, alpha=1/20., norm=False, **kwargs):
    
    # Require mapName input
    if not mapName:
        raise SystemExit('mapName parameter not given!')

    # Intelligent masking
    if mask:
        if type(mask) == float:
            decmax = mask
        else:
            decmax = -25.

    # Warn for multipole fit
    if multi and (decmax > -25):
        print('WARN: multipole fitter applied with mask at %s' % decmax)
        print('Suggested mask value: -25')

    # Collect passed keyword arguments for easy future use
    opts = locals()
    kwargs = opts.pop('kwargs')     # Catches unnecessary keyword args

    # Read in (multiple) input files
    data, bg, local = np.sum([hp.read_map(f, range(3))
            for f in inFiles], axis=0)

    # Option for multipole subtraction
    fix_data, fix_bg = None, None
    if fix_multi:
        # Establish paths for analysis storage of maps
        ftot = '{}/IC86_24H_sid.fits'#.format(ani.maps)
        fix_data, fix_bg = hp.read_map(ftot, range(2))
    if multi:
        data = multi_subtraction(multi, data, bg, fix_data=fix_data,
                                 fix_bg=fix_bg, **opts)

    # Option for top-hat smoothing radius
    if smooth != 0:
        data_wsq = smoothMap(data, wtsqr=True, **opts)
        bg_wsq = smoothMap(bg, wtsqr=True, **opts)
        data = smoothMap(data, **opts)
        bg = smoothMap(bg, **opts)

    # Return desired map type
    if mapName == 'data':
        m = data
    elif mapName == 'bg':
        m = bg
    elif mapName == 'sig':
        m = LMSignificance(data, bg, alpha, data_wsq, bg_wsq)
    elif mapName == 'relint':
        with np.errstate(invalid='ignore', divide='ignore'):
            m = (data-bg) / bg
    elif mapName == 'relerr':
        with np.errstate(invalid='ignore', divide='ignore'):
            m = (data/bg) * sqrt(1/data + alpha/bg)
    elif mapName == 'fit':
        m = multifit(2, data, bg, **opts)
    else:
        raise SystemExit('Unrecognized mapName: %s' % mapName)

    # Eliminate nan's and mask
    m[np.isnan(m)] = 0
    m = maskMap(m, decmin, decmax)

    return m



