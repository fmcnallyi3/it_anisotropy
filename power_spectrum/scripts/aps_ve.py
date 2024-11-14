#!/usr/bin/env python
# coding: utf-8

import argparse
import glob
import os,sys


import healpy
import healpy as hp
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# Import standard analysis paths from directories.py in parent directory
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from mapFunctions import directories as ani
import mapFunctions.map_functions as mf
from mapFunctions.plots import medianEnergy




def omega(thetamin,thetamax):
    return 2*np.pi*(np.cos(thetamin)-np.cos(thetamax))


def make_iso(file,ss=100,lmax=20,desc="iso"):
    bgMap = mf.getMap([file], mapName = 'bg', smooth = 0)
    #manual masking
    weight = mf.maskMap(bgMap, -90., -25.)
    #sets masked pixels to 0
    weight[weight==hp.UNSEEN] = 0
    
    fakeCl = np.zeros((ss, lmax+1))

    #option 2: divides the bg map by the number of pixels, then multiples it by the number of nonmasked pixels
    #bg map = bg map/ sum of map pixels
    weight /= weight.sum()
    #bg map = bg map * sum of non zero pixels
    weight *= (weight != 0).sum()
    
    for n in range(ss):
        #possion distribution- creates samples from probabillity of an event happening from the bkg map
        dummyMap = np.random.poisson(bgMap)
        #calculates the relative intensity from the poisson distribution 
        relInt = np.nan_to_num((dummyMap/bgMap - 1))
        #multiplies fake relative intensity map w/ weighting
        weightedMap = relInt * weight
        avg = np.average(weightedMap)
        q = weightedMap - avg
        
        #takes the average of the weighted fake RelInt map
        fCl = hp.anafast(q,lmax=lmax)
        
        fakeCl[n] = fCl

    #makes arrays of fake Cls and standard deviation

    fCl3SigA_l = [] 
    fCl3SigB_l  = [] 

    #appends Cls to different sigmas
    for i, fCl in enumerate(fakeCl.T):
        fCl3SigA = np.percentile(fCl, 2.5)
        fCl3SigB = np.percentile(fCl, 97.5)

        fCl3SigA_l += [fCl3SigA]
        fCl3SigB_l += [fCl3SigB]


    fCl3SigA = np.asarray(fCl3SigA_l)
    fCl3SigB = np.asarray(fCl3SigB_l)

    fCl3SigA = fCl3SigA[1:]
    fCl3SigB = fCl3SigB[1:]
    return fCl3SigA,fCl3SigB

def error_bars(file,ss = 100, desc="error bars"):

    #divides the bg map by the number of pixels, then multiples it by the number of nonmasked pixels
        #bg map = bg map/ sum of map pixels
        
    dataMap = mf.getMap([file], mapName = 'relint', mask = True, smooth = 0)
    bgMap = mf.getMap([file], mapName = 'bg', mask = True, smooth = 0)
    bgMap[bgMap == hp.UNSEEN] = 0
    
    bgMap /= bgMap.sum()
        #bg map = bg map * sum of non zero pixels
    bgMap *= (bgMap != 0).sum()
        #for data set
    w = dataMap*bgMap
    avg = np.average(w)
    h = w - avg

    #calculates power spectrum
    y = hp.anafast(h, lmax = 3*64-1)

    #error bars
    #paramaters
    #should be the same for both maps
    npix = dataMap.size
    nside = hp.npix2nside(npix)
    lmax = 3*nside - 1

        
    fakeCl = np.zeros((ss, lmax+1))
    for n in range(ss):
        fakeRL = hp.synfast(y, nside = nside, verbose=False)
        fCl = hp.anafast(fakeRL)
        fakeCl[n] = fCl


    #makes arrays of fake Cls and standard deviation   
    fCl02_l, fCl16_l, fCl84_l, fCl98_l  = ([] for i in range(4))
    
    #appends Cls to different sigmas
    for i, fCl in enumerate(fakeCl.T):
    
        fCl02 = np.percentile(fCl, 2.5)
        fCl16 = np.percentile(fCl, 16)
        fCl84 = np.percentile(fCl, 84)
        fCl98 = np.percentile(fCl, 97.5)
        
        fCl02_l += [fCl02]
        fCl16_l += [fCl16]
        fCl84_l += [fCl84]
        fCl98_l += [fCl98]

    fCl02 = np.asarray(fCl02_l)
    fCl16 = np.asarray(fCl16_l)
    fCl84 = np.asarray(fCl84_l)
    fCl98 = np.asarray(fCl98_l)
    

    #calculates standard deviation
    #for map w/ BF
    fCl02[fCl02 < 0] = 1e-11
    fCl16[fCl16 < 0] = 1e-11
    dCl16 = y - fCl16
    dCl84 = fCl84 - y
    dCl = [ dCl16, dCl84 ]
    return dCl

    


def noise(nevents, dmin=-np.radians(70),dmax=np.radians(70),nside=64):
    
    """Set pixels outside the region of interest to UNSEEN"""

    npix = hp.nside2npix(nside)
    minPix = hp.ang2pix(nside, np.radians(90) - dmax, 0.)
    maxPix = hp.ang2pix(nside, np.radians(90) - dmin, 0.)
    
    vpix = maxPix - minPix
    m = np.ones(npix)*healpy.UNSEEN
    m[minPix:maxPix] = (np.random.rand(vpix)+1)*nevents/vpix
    
    thetamin = -dmax+np.pi*.5
    thetamax = -dmin+np.pi*.5
    
    
    o = omega(thetamin,thetamax)
    #osqr = o*o*.25/np.pi
    nsum = 0.
    for ipix in range(npix):
        if m[ipix] == hp.UNSEEN or m[ipix] <= 0:
            continue
        theta, phi = hp.pix2ang(nside, ipix)
        if theta > thetamin and theta < thetamax:
            nsum+=1./m[ipix]*(o/(1.*npix))**2/4./np.pi
        
    return nsum


def getAPS(files, lmax=None, mArgs={'mask':True,'smooth':0}):

    # mArgs can take in any keyword argument for getMap
    relint = mf.getMap(files, mapName='relint', **mArgs)
    weight = mf.getMap(files, mapName='bg', **mArgs)

    # Default value for lmax
    if lmax == None:
        nside = hp.npix2nside(len(relint))
        lmax = 3*nside - 1

    # Normalize weight map: divide by average of unmasked pixels
    weight[weight==hp.UNSEEN] = 0
    weight /= np.average(weight[weight!=0])
    # Apply to relint, and shift so average is 0
    relint *= weight
    relint = relint - np.average(relint)

    # Calculate power spectrum
    l = np.arange(lmax+1)
    Cl = hp.anafast(relint, lmax=lmax)
    
    return l, Cl


""" Accepts a nested list of files [[f0, f1], [f2, f3], etc.] """
def getAPSvE(filegroups, 
            dClfiles=[], isofiles=[],  lmax=None, multi=None,ss=100):

    mArgs = {'mask':True, 'smooth':0}
        
    el = []
    eCl = []
    edCl = []
    enoise = []
    eiso = {}
  

    for i, files in enumerate(filegroups):
        
        ebin = files[0].split("_")[-1].strip(".fits")
        l, Cl = getAPS(files, lmax=lmax, mArgs=mArgs)
        el.append(l)
        eCl.append(Cl)
        

        # Load uncertainties (dCl) if available        
        if dClfiles != []:
            #dCl = np.load(dClfiles[i][0], allow_pickle=True)
            #dCl = dCl.item()
            #edCl.append(dCl['relint'])       
            dCl = np.loadtxt(dClfiles[i][0])
            edCl.append(dCl)       
            
        else:
            edCl.append(error_bars(files[0],ss = ss,desc=ebin+" errors"))

        
        ndata = 0
        
        data = hp.read_map(files[0],0)
        weight = mf.maskMap(data, -90., -25.)
        #sets masked pixels to 0
        weight[weight==hp.UNSEEN] = 0
        ndata = sum(weight)
                
        enoise.append( noise(ndata,dmin=np.radians(-70),dmax=np.radians(-20))*10 )
        if -1 not in eiso:
           eiso[-1]=[]
        if 1 not in eiso:
           eiso[1]=[]
 
           
        if isofiles != []:
            iso = np.load(isofiles[i][0], allow_pickle=True)
            iso = iso.item()
            eiso[-1].append(iso[-2])
            eiso[1].append(iso[2])
        else:

            siga,sigb = make_iso(files[0],ss=ss,lmax=25,desc=ebin+" iso")
            eiso[-1].append(siga)
            eiso[1].append(sigb)



    return el,eCl,edCl, np.array(enoise),eiso






if __name__ == "__main__":

    import argparse
    # Establish standard paths to analysis data
    ani.setup_input_dirs()

    p = argparse.ArgumentParser(
            description='Makes daily healpix maps using time-scrambling code')

    p.add_argument('-p', '--prefix', dest='prefix', 
            default = ani.maps,
            help='input file location')

    p.add_argument('-s', '--samples', dest='samples', 
            default = 0, type=int,
            help='Number of random samples for calculating errors')

    p.add_argument('-l', '--lmax', dest='lmax', 
            default = 20 ,type=int,
            help='largest \\ell value to evaluate')

    p.add_argument('-o', '--outputfile', dest='output', 
            default = 'Cl_v_Energy.pdf' ,
            help='Name of output file')

    args = p.parse_args()


    #get all energy binned files
    files = sorted(glob.glob(f'{args.prefix}/IC86_N10_sid_*GeV*.fits'))
    energies = [i for f in files for i in f.split('_') if 'GeV' in i]
    energies = [i.replace('.fits', '') for i in energies]
    iso = []
    stat = []
    sys = []
    if not args.samples > 0:
        for e, m in zip(energies, files):

            sys.append( f'{ani.aps}/sys_IC86_{e}_10000_S0.txt')
            stat.append(f'{ani.aps}/stat_IC86_{e}_10000_S0.txt')
            iso.append(f'{ani.aps}/iso_IC86_{e}_100000_S0.npy')
            emin, emax = e.split('-')
            emin = float(emin)
            emax = float(emax[:-3])     # Exclude the "GeV" from the name
            label = '_'.join(medianEnergy(emin, emax).split(' '))

        iso = [[f] for f in iso]
        stat = [[f] for f in stat]
        sys = [[f] for f in sys]


    files = [[f] for f in files]
    decmin = -np.radians(80)
    decmax = -np.radians(20)

        #Calculate angular power spectrum vs. energy
    l,cl,dcl,eno,iso = getAPSvE(files,stat,iso, lmax=args.lmax,ss=args.samples)


    #Create figure
    fig= plt.figure(figsize=(12,6))
    ax = plt.subplot(111)

    #Create colormap
    cmap = matplotlib.cm.get_cmap('Spectral')
    def rgb_to_hex(rgb):
        return matplotlib.colors.to_hex(np.array(rgb)/256., keep_alpha=False)


    bins = range(len(l))
    elabels = np.log10(np.array([13,24,42,67,130,240,470,1.5e3,5.3e3])*1e3)

    #x in center of bin
    xerr = np.log10(elabels)*.5

    cls = []
    dcls = []
    symbols = ['o','s','^','v','>','*','p','d','P','X']

    # symbol index
    si = 0 

    ell_vals = [1,2,3,4,6,11,20]
    gradient = np.linspace(0, 1, len(ell_vals))
    for i in ell_vals:
        rgba_color = cmap(gradient[len(ell_vals)-1-si],bytes=True)
        color = rgb_to_hex(rgba_color)
        cli = np.zeros(len(elabels))

        isoi ={}
        dcli = [np.zeros(len(elabels)) for j in range(2)]
        if type(i) == int:
            cli = np.array([icl[i] for icl in cl])
            dcli[0] = np.array([icl[0][i] for icl in dcl])
            dcli[1] = np.array([icl[1][i] for icl in dcl])

            for key in iso: 
                isoi[key] = np.array([icl[i-1] for icl in iso[key]])
        else:
            for j in i:
                cli += np.array([icl[j] for icl in cl])
                dcli += np.array([icl[j]**2 for icl in dcl])

            cli /= len(i)
            dcli = np.sqrt(dcli)
        

        
        label = "$\ell=%s$"%str(i)
        if type(i) != int:
            label = "$\ell=%s-%s$"%(i[0],i[-1])
            
        p = ax.errorbar(elabels, cli, yerr=[dcli[0],dcli[1]], #[cli*(1.-0.5*dcli),cli*(1+0.5*dcli)], 
                fmt=symbols[si%len(symbols)], label=label,color=color,
                ecolor=color,markersize=10,markerfacecolor=color,markeredgecolor="black")
        
        ax.fill_between(elabels, isoi[-1], isoi[1], lw=0,alpha=0.4,  interpolate=True, color=color)

        si += 1

    ax.plot(elabels,np.array(eno)*1,"--",label="noise", color="black")


    # Labels for main axes
    plt.xlabel(r'$\log_{10}$($E$/GeV)',fontsize=14)
    plt.ylabel(r'$\tilde{C}_{\ell}$',fontsize=18)
    plt.yscale('log')

    plt.ylim(5e-12,2e-6)
    plt.xlim(4,6.8)
    # Hides gridlines(?)
    for item in (ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(16)

    plt.legend()
    plt.grid(visible=False) 
    plt.show()
    fig.savefig(args.output, dpi=100)


