#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py3-v4.1.1/icetray-start
#METAPROJECT: icetray/stable

import subprocess, argparse, re
import numpy as np
from glob import glob
import os, sys

current = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current)
from mapFunctions import directories as ani
from mapFunctions.plots import medianEnergy

def getEbins():
    return [4, 4.25, 4.5, 4.75, 5, 5.25, 5.5, 6, 6.5, 100]


def getEnergyMaps(config, ebins=getEbins()):

    ani.setup_input_dirs(verbose=False)
    mapFiles = sorted(glob(f'{ani.maps}/{config}_N10_sid_*GeV.fits'))
    erange = [re.search(r'_([\d\.]+)-([\d\.]+)GeV', f).groups() \
            for f in mapFiles]
    emins, emaxs = np.transpose(erange).astype(float)

    # Groups files if desired energy bins are larger than map bins
    fileList = []
    for i in range(len(ebins)-1):
        fileList += [[f for j, f in enumerate(mapFiles) \
                if emins[j]>=ebins[i] and emaxs[j]<=ebins[i+1]]]

    return fileList


if __name__ == "__main__":

    # General options
    p = argparse.ArgumentParser(
            description='Makes all plots for anisotropy paper')
    p.add_argument('--all', dest='all',
            default=False, action='store_true',
            help='Make all plots')
    p.add_argument('--saveFITS', dest='saveFITS',
            default=False, action='store_true',
            help='Save maps as FITS files in addition to plots')
    p.add_argument('--ext', dest='ext',
            default='png',
            help='Output extension for plots')

    # Skymaps
    p.add_argument('--largesmall', dest='largesmall',
            default=False, action='store_true',
            help='Large and small scale structure maps for IceCube')
    p.add_argument('--ebins', dest='ebins',
            default=False, action='store_true',
            help='IceCube maps binned in energy')
    p.add_argument('--solar', dest='solar',
            default=False, action='store_true',
            help='Solar dipole maps')

    # Optional variants for skymaps
    p.add_argument('--polar', dest='polar',
            default=False, action='store_true',
            help='IceCube maps binned in energy (polar view)')
    p.add_argument('--cmap', dest='cmap',
            default=False, action='store_true',
            help='Changes the color scale to red->white->blue (seismic)')

    # Analysis plots
    p.add_argument('--powerspec', dest='powerspec',
            default=False, action='store_true',
            help='Power spectrum plot')
    p.add_argument('--toy-powerspec', dest='toypowerspec',
            default=False, action='store_true',
            help='Toy MC Power spectrum plot')
    p.add_argument('--powerspec-ve', dest='powerspec_ve',
            default=False, action='store_true',
            help='Power spectrum vs energy')

    p.add_argument('--dipole', dest='dipole',
            default=False, action='store_true',
            help='Plot dipole phase as a function of energy')
    p.add_argument('--reco', dest='reco',
            default=False, action='store_true',
            help='Plot table used for IC energy reconstructions')
    p.add_argument('--edist', dest='edist',
            default=False, action='store_true',
            help='Plot true energy distributions for reco energy bins')

    # One-dimensional projections
    p.add_argument('--proj', dest='proj',
            default=False, action='store_true',
            help='Plot 1D projection for sid + solar')
    p.add_argument('--projannual', dest='projannual',
            default=False, action='store_true',
            help='Plot annual 1D projections for sid + anti')
    p.add_argument('--projerr', dest='projerr',
            default=False, action='store_true',
            help='Plot 1D projection for anti + ext')
    p.add_argument('--projcomp', dest='projcomp',
            default=False, action='store_true',
            help='Compare 1D projections as a function of time')
    p.add_argument('--projenergy', dest='projenergy',
            default=False, action='store_true',
            help='1D projections for each energy bin')

    # Stability checks
    p.add_argument('--mapcheck', dest='mapcheck',
            default=False, action='store_true',
            help='Plot daily map counts for each detector config and map type')
    p.add_argument('--timegaps', dest='timegaps',
            default=False, action='store_true',
            help='Plot visualizations of time gaps')

    # Analysis review requests
    # ...

    args = p.parse_args()

    # Load common input and output paths
    ani.setup_input_dirs(verbose=False)
    ani.setup_output_dirs(verbose=False)

    # Plots/Options to omit when reproducing all
    omits = ['cmap','polar','ext','saveFITS','timegaps','mapcheck']
    if args.all:
        for arg in vars(args):
            if arg not in omits:
                setattr(args, arg, True)

    
    ## ==================================================================== ##
    ## Skymaps

    mapList  = []
    cmd = f'{current}/mapFunctions/plotFITS.py'
    defArgs  = f'--half --outDir {ani.figs} --ext {args.ext}'
    #defArgs += ' --prelim'  # Include 'preliminary' text on images
    if args.saveFITS:
        defArgs += ' --saveFITS'

    # Large- and small-scale structure

    # Default arguments (adjusted mask for low statistics near horizon)
    ls_args = '-D -30 --gplane'

    # Split into low- and high-energy versions
    low_e = f'{ani.maps}/IC86_N10_sid_4-4.25GeV.fits'
    hi_e  = f'{ani.maps}/IC86_N10_sid_5.5-100GeV.fits'
    #low_e, _, hi_e = [' '.join(fileList) for fileList in
    #        getEnergyMaps('IC86', ebins=[4,4.25,5.5,100])]

    # Low-energy (1st energy bin)
    out = 'IC86_lowE'
    # Relative intensity
    base = f'{low_e} -n relint -S 5'
    a  = [f'{base} -s 3 -m -1.5 -M 1.5 --customOut {out}_relint']
    a += [f'{base} -s 4 -m -4 -M 4 --multi 2 --customOut {out}_relint_l2']
    # Significance
    base = f'{low_e} -n sig -S 5'
    a += [f'{base} -x 5 -m -65 -M 45 --customOut {out}_sig']
    a += [f'{base} -x 5 -m -16 -M 16 --multi 2 --customOut {out}_sig_l2']

    # High-energy (Top four energy bins)
    out = 'IC86_hiE'
    # Relative intensity
    base = f'{hi_e} -n relint -S 20'
    a += [f'{base} -s 3 -m -1.5 -M 1.5 --customOut {out}_relint']
    a += [f'{base} -s 4 -m -5 -M 5 --multi 2 --customOut {out}_relint_l2']
    # Significance
    base = f'{hi_e} -n sig -S 20'
    a += [f'{base} -x 5 -m -14 -M 7 --customOut {out}_sig']
    a += [f'{base} -x 3 -m -5 -M 5 --multi 2 --customOut {out}_sig_l2']

    if args.largesmall:
        mapList += [f'{a_i} {ls_args}' for a_i in a]


    # Anisotropy as a function of energy

    # Collect maps & set default arguments
    e_maps = sorted(glob(f'{ani.maps}/IC86_N10_sid_*GeV.fits'))
    e_maps = [[f] for f in e_maps]
    #e_maps = getEnergyMaps('IC86')
    e_args = '--mask -S 20'

    # Peak significance values for energy bins
    # 4-4.25: -180-130
    # 4.25-4.5: -133-97
    # 4.5-4.75: -69-50
    # 4.75-5: -27-17
    # 5-5.25: -12-8
    # 5.25-5.5: -11-8
    # 5.5-100: -13.4-6.5
    # 5.5-6: -12-6.3
    # 6-6.5: -6.5-4.2
    # 6.5-100: -3.9-sub-3
    sig_scales = [[-190,140], [-140,100], [-70,50], [-30,20], [-12,8], [-12,8], [-13,7], [-12,8], [-6,5], [-5,5]]

    a = []
    eMins = [float(re.split('_|-|GeV', files[0])[-3]) for files in e_maps]
    eMaxs = [float(re.split('_|-|GeV', files[0])[-2]) for files in e_maps]
    #eMins = getEbins()[:-1]
    for i, maps in enumerate(e_maps):
        maps = ' '.join(maps)   # plotter can combine data from multiple maps
        minmax = 3 if eMins[i]>=6 else 1
        if eMins[i] < 6 and eMaxs[i] == 100:
            minmax = 1.5        # special case for combined HE bin
        tempArgs = f'{maps} -n relint -s 3  -m -{minmax} -M {minmax}'
        a += [tempArgs]

        # Significance
        threshold = 3 if eMins[i]>=6 else 5
        m, M = sig_scales[i]
        tempArgs = f'{maps} -n sig -x {threshold} -m {m} -M {M}'
        a += [tempArgs]

    if args.ebins:
        mapList += [f'{a_i} {e_args}' for a_i in a]


    # Solar dipole (uses same default arguments as energy-binned)
    # Change to 5 degree smoothing like sidereal?
    mapFile = f'{ani.maps}/IC86_N10_solar.fits'
    a  = [mapFile+' -n relint -S 5 -s 4 -m -3 -M 3 --mask']
    a += [mapFile+' -n sig -S 5 -x 5 -m -60 -M 60 --mask']

    if args.solar:
        mapList += [f'{a_i} {e_args}' for a_i in a]


    # Variants to produce in addition to original maps
    if args.polar:
        variants = [f'{f} --polar' for f in mapList if 'IC86_N10' in f]
        mapList += variants
    if args.cmap:
        variants = [f'{f} --cmap seismic' for f in mapList]
        mapList += variants


    # Apply default arguments and plot command function
    mapList = [f'{cmd} {a} {defArgs}' for a in mapList]
    for a in mapList:
        # Custom adaptation for polar maps
        if 'polar' in a:
            a = a.replace(' --half', '')
            a = a.replace(' --gplane', '')
        proc = subprocess.Popen(a.split(' '))


    ##=========================================================================
    ## Other analysis plots

    # Dipole phase as a function of energy
    # Outdated IceCube-only version
    #out = f'{ani.figs}/IC86_Dipole_Only.{args.ext}'
    #cmd = f'{current}/mapFunctions/phasePlot.py'
    #a = f'{cmd} -f energy -l 3 -o {out} --offset 90 -n 72 -S 4'
    #a = f'{cmd} -f energy -l 4 -o {out} --offset 90'
    out = f'{ani.figs}/IC86_Dipole.{args.ext}'
    cmd = f'{current}/mapFunctions/phasePlotExp.py'
    a = f'{cmd} -f energy -l 3 -o {out} -S 4 --fit-2d --fov-correction'
    if args.dipole:
        print(a)
        proc = subprocess.Popen(a.split(' '))


    # Power spectrum 
    # Commands for making uncertainties:
    #   ./maker.py --ebins --sys -n 10000
    #   ./maker.py --ebins --stat -n 10000
    #   ./maker.py --ebins --iso -n 100000
    cmd = f'{current}/scripts/aps.py'

    # Power spectrum split by energy
    out = f'{ani.figs}/IC86_powerspec.{args.ext}'
    #e_maps = [f[0] for f in getEnergyMaps('IC86')]
    e_maps = sorted(glob(f'{ani.maps}/IC86_N10_sid_*GeV.fits'))
    energies = [i for f in e_maps for i in f.split('_') if 'GeV' in i]
    energies = [i.replace('.fits', '') for i in energies]

    first = True
    for e, m in zip(energies, e_maps):

        sys = f'{ani.aps}/sys_IC86_{e}_10000_S0.txt'
        stat = f'{ani.aps}/stat_IC86_{e}_10000_S0.txt'
        iso = f'{ani.aps}/iso_IC86_{e}_100000_S0.npy'
        e_out = out.replace('powerspec', f'powerspec_{e}')
        emin, emax = e.split('-')
        emin = float(emin)
        emax = float(emax[:-3])     # Exclude the "GeV" from the name
        label = '_'.join(medianEnergy(emin, emax).split(' '))

        a  = f'{cmd} -f {m} --syserr {sys} --staterr {stat} --iso {iso}'
        a += f' -o {e_out} -l {label}'

        # Custom behavior for all plots after the first energy bin
        if not first:
            a += ' --mute_iso_labels'
        first = False

        if args.powerspec:
            proc = subprocess.Popen(a.split(' '))

    # Angular power for select spherical harmonic modes
    cmd = f'{current}/powerspec/aps_ve.py'
    out = f'{ani.figs}/IC86_powerspec_vs_energy.{args.ext}'
    a  = f'{cmd} -o {out} -l 20'
    if args.powerspec_ve:
        print(a)
        proc = subprocess.Popen(a.split(' '))

    ## ==================================================================== ##
    ## Simulation

    cmd = f'{current}/icesim/plots.py'

    # Reconstructed energy table (rainbow plot) with splines applied
    out = f'{ani.figs}/IC86_Median_Energy_Spline.{args.ext}'
    a = f'{cmd} --rainbow -i {ani.sim_hist} -o {out} --spline'
    if args.reco:
        proc = subprocess.Popen(a.split(' '))

    # Reconstructed energy table (rainbow plot) without splines applied
    out = f'{ani.figs}/IC86_Median_Energy.{args.ext}'
    a = f'{cmd} --rainbow -i {ani.sim_hist} -o {out}'
    if args.reco:
        proc = subprocess.Popen(a.split(' '))

    # Energy distribution plot
    out = f'{ani.figs}/IC86_Energy_Distributions.{args.ext}'
    ebins = ' '.join([str(i) for i in getEbins()])
    a = f'{cmd} --edist -i {ani.sim_hist} -o {out} --ebins {ebins}'
    if args.edist:
        proc = subprocess.Popen(a.split(' '))

    # Energy distribution for low- and high-energy splits
    out = f'{ani.figs}/IC86_Energy_Distributions_1.{args.ext}'
    ebins = '4 4.25 5.5 100'
    a = f'{cmd} --edist -i {ani.sim_hist} -o {out} --ebins {ebins} --nomids'
    if args.edist:
        proc = subprocess.Popen(a.split(' '))

    ## Toy APS
    cmd = f'{current}/powerspec/toy.py'
    out = f'{ani.figs}/toy_aps.{args.ext}'
    lmax = 30
    a = f'{cmd} --lmax {lmax} -o {out}'
    if args.toypowerspec:
        proc = subprocess.Popen(a.split(' '))


    ## ==================================================================== ##
    ## One-Dimensional Projections

    cmd = f'{current}/mapFunctions/proj1d.py'

    # One-dimensional projection (sidereal and solar)
    out = f'{ani.figs}/IC86_proj1d.{args.ext}'
    mapTypes = ['sid','solar']
    maps = ' '.join([f'{ani.maps}/IC86_N10_{t}.fits' for t in mapTypes])
    a = f'{cmd} {maps} -z -o {out} --labels method -L -S 4'
    if args.proj:
        proc = subprocess.Popen(a.split(' '))

    # One-dimensional projection (sidereal only with best-fit parameters)
    out = f'{ani.figs}/IC86_proj1d_sid.{args.ext}'
    m = f'{ani.maps}/IC86_N10_sid.fits'
    a = f'{cmd} {m} -z -o {out} --fit 3 -S 4'
    if args.proj:
        proc = subprocess.Popen(a.split(' '))

    # 1D projection v. energy (sidereal only with best-fit parameters)
    e_maps = [f[0] for f in getEnergyMaps('IC86')]
    energies = [i for f in e_maps for i in f.split('_') if 'GeV' in i]
    energies = [i.replace('.fits', '') for i in energies]
    for e, m in zip(energies, e_maps):
        out = f'{ani.figs}/IC86_proj1d_sid_{e}.{args.ext}'
        a = f'{cmd} {m} -z -o {out} --fit 3 -S 4 --flat'
        if args.projenergy:
            proc = subprocess.Popen(a.split(' '))

    # One-dimensional projections (anti-/sidereal, annual)
    annual = []
    # Anti-sidereal
    maps = sorted(glob(f'{ani.maps}/IC86-????_N10_anti.fits'))
    for m in maps:
        config = re.findall('IC86-\d{4}', m)[-1]
        out = f'{ani.figs}/annual/proj1d_anti_{config}.{args.ext}'
        annual += [f'{cmd} {m} -z -o {out} --fit 1 --flat -S 5 -m -10 -M 10']
    # Sidereal
    maps = sorted(glob(f'{ani.maps}/IC86-????_N10_sid.fits'))
    for m in maps:
        config = re.findall('IC86-\d{4}', m)[-1]
        out = f'{ani.figs}/annual/proj1d_sid_{config}.{args.ext}'
        annual += [f'{cmd} {m} -z -o {out} --fit 3 -S 4']
    if args.projannual:
        for a in annual:
            proc = subprocess.Popen(a.split(' '))


    # Uncertainty in one-dimensional projection
    out = f'{ani.figs}/IC86_proj1d_err.{args.ext}'
    mapTypes = ['anti','ext']
    maps = ' '.join([f'{ani.maps}/IC86_N10_{t}.fits' for t in mapTypes])
    a = f'{cmd} {maps} -z -o {out} --labels method -L -S 5'
    if args.projerr:
        proc = subprocess.Popen(a.split(' '))

    # One-dimensional projection (shared x-axis)
    out = f'{ani.figs}/IC86_proj1d_err_shared.{args.ext}'
    a = f'{cmd} {maps} -z -o {out} --split --labels method -S 5'
    if args.projerr:
        proc = subprocess.Popen(a.split(' '))

    # Time variation in 1D projection by year
    files = ' '.join(sorted(glob(f'{ani.maps}/IC86-*_N10_sid.fits')))
    out = f'{ani.figs}/IC86_proj1d_comp.{args.ext}'
    a = f'{cmd} {files} -z -o {out} --labels configs --offset --full -L -S 4'
    a += f' --stripes --midticks'   # --rotated
    if args.projcomp:
        print(a)
        proc = subprocess.Popen(a.split(' '))


    ## ==================================================================== ##
    ## Stability Checks

    # Event checks for maps
    cmd = f'{current}/stability/mapCheck.py'
    #a = f'{cmd} --everything -o {ani.figs}'
    if args.mapcheck:
        #proc = subprocess.Popen(a.split(' '))
        # Produce the rate version too
        a = f'{cmd} --everything -o {ani.figs} --rate'
        proc = subprocess.Popen(a.split(' '))

    # Time gaps
    cmd = f'{current}/stability/timegaps/plotter.py'
    #a = f'{cmd} --config --season --largestgap --cumulative -o {ani.figs}'
    a = f'{cmd} --config --season --largestgap -o {ani.figs}'
    if args.timegaps:
        proc = subprocess.Popen(a.split(' '))
        # Also produce all plots with gaps between runs excluded
        a = f'{cmd} --config -o {ani.figs} --rungaps'
        proc = subprocess.Popen(a.split(' '))

    print("All plots have been created!")



