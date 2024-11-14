#!/usr/bin/env python
# coding: utf-8


import sys, os, os.path
import matplotlib
import matplotlib.pyplot as plt
import healpy as hp
import numpy as np
import json
from matplotlib.ticker import FuncFormatter, MaxNLocator

# Import standard analysis paths from directories.py in parent directory
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import directories as ani


class Point:
    def __init__(self, energy, A1=0, A1errHi=0,A1errLo=0,alpha=0,alpha_err=0,upperlim=0,lowerlim=0):
        self.energy = energy
        self.A1 = A1
        self.A1errHi = A1errHi
        self.A1errLo = A1errLo
        self.alpha = alpha
        self.alpha_err = alpha_err
        self.upperlim = upperlim
        self.lowerlim = lowerlim

class Experiment:
    def __init__(self, name, data=[], scale=1.0,color='black',shape='^', 
            markersize=1,facecolor=None,uplim=False, DOI=None,include=True):

        self.name = name
        self.data = [Point(**d) for d in data]
        self.scale = scale
        self.color = color
        self.shape = shape
        self.markersize = markersize
        self.facecolor = color
        self.uplim = uplim
        self.DOI = DOI
        self.include = include
        if self.facecolor:
            self.facecolor=facecolor


#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py3-v4.1.1/icetray-start
#METAPROJECT icetray/stable

import healpy as hp
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import stats
import glob, argparse, os

from icesim.histFunctions import ebin_params
from mapFunctions.map_functions import getMap
from proj1d import getRelInt


def getEbins():
    #return [4, 4.25, 4.5, 4.75, 5, 5.25, 5.5, 6, 6.5]
    return [4, 4.25, 4.5, 4.75, 5, 5.25, 5.5, 6, 6.5, 100]


def cosinefit(x, *p):
    k = 2*np.pi / 360       # Wavenumber (assumes x in degrees)
    l = len(p) // 2         # Multipole number of fit
    return sum([p[2*i] * np.cos((i+1)*k*x - p[2*i+1]) for i in range(l)])

# Cosine function with fixed base wavelength of 360 degrees
def multipole(x, *p):
    k = 2*np.pi/360         # Wavenumber (assumes x in degrees)
    l = int(len(p) / 2)    # Multipole number of fit
    return sum([p[2*i] * np.cos((i+1)*k*x - p[2*i+1]) for i in range(l)])



def multipoleFit(x, y, l, sigmay, fittype='cos'):

    # Guess at best fit parameters
    amplitude = (3./np.sqrt(2)) * np.std(y)
    phase     = 0
    p0 = [amplitude, phase] * l

    # Do best fit
    popt, pcov = curve_fit(multipole, x, y, p0, 
                           sigma=sigmay, absolute_sigma=True)
    chi2 = sum((y - multipole(x, *popt))**2 / sigmay**2)
    ndof = x.size - popt.size
    pvalue = 1 - stats.chi2.cdf(chi2, ndof)
    perr = np.sqrt(np.diag(pcov))

    return popt, perr, chi2, ndof, pvalue


def multipoleYlm(l):
    import scipy.special
    tmp = np.power(2,l)*scipy.special.factorial(l)
    return np.sqrt(scipy.special.factorial(2*l+1)*.24/np.pi)/tmp

def multipole2dfunc(l,nside):

    def multipole2d(ipix, *p):
        k = np.pi/180         # Wavenumber (assumes x in degrees)

        ra,dec = hp.pix2ang(nside, ipix,lonlat=True)

        horizontal = sum([p[2*i] * np.power(np.cos(k*dec),i+1) * np.cos((i+1)*k*ra - p[2*i+1]) for i in range(l)])
        return horizontal

    return multipole2d


def multipoleFit2d(f,l,nside_out=None, **opts):
    import scipy

    f = [f] if type(f) != list else f

    relint = getMap(f, mapName='relint', **opts)
    relerr = getMap(f, mapName='relerr', **opts)
    variance = np.power(relerr,2)
    if nside_out:
        relint = hp.ud_grade(relint, nside_out)
        variance= hp.ud_grade(variance, nside_out,power=2)
        relerr=np.sqrt(variance)

    npix = relint.size
    nside = hp.npix2nside(npix)
    minpix = hp.ang2pix(nside,0,-30,lonlat=True)
    pixels = range(minpix,npix)
    maxphase=2*np.pi

    # Guess at best fit parameters
    amplitude = 1
    phase     = 1
    p0 = [amplitude, phase] * l

    # Define bounds
    b0 = [0,0] * l
    b1 = [np.inf,maxphase] * l
    
    fitfunc = multipole2dfunc(l,nside)
    popt, pcov = curve_fit(fitfunc,
        pixels,
        relint[pixels],
        p0,
        #bounds=(b0,b1), #for some reason the combination of b0 and p0 doen't work
        sigma=relerr[pixels], absolute_sigma=True
        )
    chi2 = sum((relint[pixels] - fitfunc(pixels, *popt))**2 / relerr[pixels]**2)
    ndof = len(pixels) - popt.size
    pvalue = 1 - stats.chi2.cdf(chi2, ndof)
    perr = np.sqrt(np.diag(pcov))

    return popt, perr, chi2, ndof, pvalue



if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='')
    p.add_argument('-f', '--files', dest='files',
            default='energy',
            choices=['energy','config','comp','solar'],
            help='Choose from presets for files to run over')
    p.add_argument('-n', '--nbins', dest='nbins', 
            type=int, default=24,
            help='Number of bins for the 1D fit')
    p.add_argument('-o', '--out', dest='out',
            default="12year-dipole.pdf",
            help="Option to write to file")
    p.add_argument('-S', '--scale', dest='scale',
            type=int, default=4,
            help='Exponential scale for multiplying y-axis')
    p.add_argument('--weight_RI', dest='weight_RI',
            default=False, action='store_true',
            help='Use unweighted average for 1D projection')
    p.add_argument('--fit-2d', dest='fit2d',
            default=False, action='store_true',
            help='Use 2d fit for l=1,2,3 instead of 1D projection')
    p.add_argument('--fov-correction', dest='fov',
            default=False, action='store_true',
            help='Correct for FoV')
    p.add_argument('-L', '--label', dest='label',
            default='IceCube (this work)',
            help='legend label for data points')
    p.add_argument('--exp-data', dest='exp_data', 
            default=f"{parent}/data/phase_amplitude_data.json",
            help='experimental data json file')
    p.add_argument('-l', '--lvalue', dest='l', type=int,
            help="Option to fix l-value for multipole fit")
    p.add_argument('--ud-grade', dest='ud_grade', type=int,default=None,
            help="Use a different nside to do 2D-fit")
    args = p.parse_args()

    phase_data_points = {}
    with open(args.exp_data,"r") as datafile:
        phase_data_points = json.load(datafile)

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
        print(f'{ani.maps}')
        files = sorted(glob.glob(f'{ani.maps}/IC86_N10_sid_*GeV*'))
        del files[6]
        print(files)
        ebins = getEbins()
        x, xL, xR, _ = ebin_params(ani.sim_hist, ebins)
        masks = [-30. for xi in x]
        masks[0] = -35.

        print("\n".join(
            ["{:.1f} ({:.1f},{:.1f}) TeV".format(
                np.power(10,x[i]-3),
                np.power(10,xL[i]-3),
                np.power(10,xR[i]-3)) for i in range(len(x)
                )
            ]))
        xL = x - xL
        xR = xR - x
        smooth = 20

    nfiles = len(files)
    lmax = int(args.nbins/2) - 1
    if lmax > 15:
        lmax = 15

    # Y-axis scale
    scale = 10**args.scale

    if args.fit2d and args.weight_RI:
       print("weight-RI makes no sense with 2d fit. Remove one of these options")
       os._exit(1)

    opts = {'mask':True, 'ramin':0., 'ramax':360., 'nbins':args.nbins}
    opts['weight_RI'] = args.weight_RI
    amp, phase, amp_err, phase_err= np.zeros((4, nfiles))
    fov_corr = 1.0
    chi2array = np.zeros((nfiles,lmax-1))
    chi2sums  = np.zeros(nfiles)
    pvals = np.zeros(nfiles)
    ndofs = np.zeros(nfiles)

    if not args.l:
        chi2array[chi2array < .7] = 100
        args.l = chi2array.sum(axis=0).argmin() + 1
        
    for i, f in enumerate(files):
        
        datum = {"energy":x[i]}
        opts["mask"] = masks[i]
        if args.fit2d: 
            popt, perr, chi2,ndof, pvalue = multipoleFit2d(f, args.l, args.ud_grade, **opts)

        else:
            ra, ri, sigmax, sigmay = getRelInt(f, **opts)
            popt, perr, chi2,ndof, pvalue = multipoleFit(ra, ri, args.l, sigmay)

            fov_corr = 1.0
            if args.fov: # Correct amplitude to account for FoV
                d1 = np.radians(-90)
                d2 = np.radians(masks[i])
                s1 = np.sin(d1)
                s2 = np.sin(d2)
                c1 = np.cos(d1)
                c2 = np.cos(d2)
                fov_corr = 2*(s1-s2)/(d1-d2 + c1*s1 - c2*s2)
            print(x[i],"GeV","fov_corr",fov_corr)

        a = np.reshape(popt, (-1,2))
        amp[i], phase[i] = a[0]
        e = np.reshape(perr, (-1,2))
        amp_err[i], phase_err[i] = e[0]
        amp[i] *= scale*fov_corr
        amp_err[i] *= scale*fov_corr
        chi2sums[i] = chi2
        ndofs[i] = ndof
        pvals[i] = pvalue

    phase_data_points[args.label] = { 
            "name":args.label,
            "shape":"H",
            "color":"blue",
            "facecolor":None,
            "markersize":1.3,
            "scale":1.0,
            "data":[]
    }


    phase *= 180/np.pi
    phase_err *= 180/np.pi

    # Deal with negative amplitudes/phases
    c0 = amp < 0
    amp[c0] *= -1.
    phase[c0] += 180
    phase[phase > 360] -= 360
    phase[phase < 0] += 360

    for i in range(len(amp)):
         phase_data_points[args.label]['data'].append( 
                {
                    "energy":pow(10,x[i]-3), # TeV
                    "A1":amp[i],"A1errHi":amp_err[i],"A1errLo":amp_err[i], 
                    "alpha":phase[i],"alpha_err":phase_err[i], 
                    "upperlim":0, "lowerlim":0
                }
         )
    print(args.label)

    
    print(["{energy:.2f}GeV".format(**e) for e in phase_data_points[args.label]['data']])
    print("A_1",", ".join(["{A1:.2f}".format(**e) for e in phase_data_points[args.label]['data']]))
    print("A_1_err",", ".join(["{A1errHi:.2f}".format(**e) for e in phase_data_points[args.label]['data']]))

    print("alpha_1", ", ".join(["{alpha:.1f} \pm {alpha_err:.1f}".format(**e) for e in phase_data_points[args.label]['data']]))
    print("Chi^2/DoF", ", ".join(["{:.2f}/{}".format(chi2sums[i],ndofs[i]) for i in range(len(chi2sums))]))
    print("reduced Chi^2", ", ".join(["{:.2f}".format(chi2sums[i]/ndofs[i]) for i in range(len(chi2sums))]))
    print("p-val", ", ".join(["{:.2g}".format(pvals[i]) for i in range(len(chi2sums))]))

    fig, axs = plt.subplots(nrows=2, ncols=1, sharex=True,figsize=(14,15))
    fig.set_tight_layout(True)
    ax1 = axs[0]
    ax2 = axs[1]
    #ax = plt.subplot(111)
    bins=np.logspace(1,8,10)
    xmin, xmax = 7e2,5e10

    for d in phase_data_points:
        detector = Experiment(**phase_data_points[d])
        fov_correction = 1.0

        if args.fov: # Correct amplitude to account for FoV
            fov_correction = detector.scale
            if fov_correction != 1.0:
                detector.name = "{} (x{:0.1f})".format(detector.name,detector.scale)

        if not detector.include: continue
        data = []
        for datum in detector.data:
                alpha = datum.alpha
                if alpha > 180: alpha = alpha - 360
                data.append((
                    datum.energy*1e3,datum.A1,datum.A1errHi,datum.A1errLo,
                    datum.upperlim,datum.lowerlim,
                    alpha,datum.alpha_err))
        dE,A,dAhi,dAlo,uplims,lolims,alpha,dalpha = zip(*sorted(data))
        dE = np.array(dE)
        A = np.array(A)*1e-1*fov_correction
        dAhi = np.array(dAhi)*1e-1*fov_correction
        dAlo = np.array(dAlo)*1e-1*fov_correction
        alpha = np.array(alpha)
        dalpha = np.array(dalpha)
        lim_mask= np.array(uplims)

        ax1.errorbar(dE, alpha, yerr=dalpha, 
                fmt='*',marker=detector.shape,
                color=detector.color,mfc=detector.facecolor,label=detector.name,
                markersize=detector.markersize*9)

        ax2.errorbar(dE,A,yerr=[dAlo,dAhi],fmt="*",marker=detector.shape, 
                color=detector.color,mfc=detector.facecolor,label=detector.name,uplims=uplims,
                markersize=detector.markersize*9)


    GC = [[0,1e14],[267.8-360,267.8-360]]
    ax1.text(xmin, GC[1][0]+8, 'Galactic Center', ha= 'left', fontsize=16)
    ax1.plot(GC[0],GC[1],'--',color='black')  
    ax2.set_yscale('log')
    plt.xscale('log')


    #plt.loglog()
    # Shrink current axis by 20%
    box = ax1.get_position()
    #ax1.set_position([box.x0, box.y0, box.width, box.height*0.7])

    ncol=5
    bbox_to_anchor=(0.495, 1.22)
    if args.fov: # Legends include scale and require more space
        ncol=4
        bbox_to_anchor=(0.495, 1.29)
    leg = ax1.legend(loc='upper center', bbox_to_anchor=bbox_to_anchor,
                            ncol=ncol, fancybox=True, shadow=True,
                            numpoints=1,fontsize=14)
    plt.xlabel("Primary Energy [GeV]",fontsize=16)
    ax1.set_ylabel(r'Phase $\alpha_1$ [$^\circ$]',fontsize=16)
    ax1.set_ylim(-200,160)
    ax2.set_ylabel("Projected Amplitude $A_1$ [$10^{-3}$]",fontsize=15)
    plt.xlim(xmin,xmax)
    ax2.set_ylim(7e-2,4e2)
    
    ax1.grid()
    ax2.grid()

    for item in (ax2.get_xticklabels() + ax2.get_yticklabels() + ax1.get_yticklabels()):
                item.set_fontsize(16)


    def format_fn(tick_val, tick_pos):
        if tick_val < 0: 
            return '%d' % (tick_val+360)
        else:
            return '%d' % tick_val

    def format_fnA(tick_val, tick_pos):
        return '%01.2f' % (tick_val)
     
        
    #ax1.set_ytickslabels( alphatickmarks )    
    ax1.yaxis.set_major_formatter(FuncFormatter(format_fn))
    #ax2.yaxis.set_major_formatter(FuncFormatter(
    #        lambda y,pos:
    #('{{:.{:1d}f}}'.format(int(np.maximum(-np.log10(y),0)))).format(y)))
    #plt.subplots_adjust(hspace=0.15)
    fig.savefig(args.out, dpi=100, bbox_inches='tight')
    plt.show()





