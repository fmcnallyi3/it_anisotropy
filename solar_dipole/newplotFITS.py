#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py3-v4.1.1/icetray-start
#METAPROJECT icetray/stable

import numpy as np
import healpy as hp
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from matplotlib.colors import LinearSegmentedColormap
from optparse import OptionParser
import sys, os, re
import warnings

# Import functions from other directories in the tree
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from mapFunctions.map_functions import getMap
from icesim.histFunctions import ebin_params

# Output paths from directories.py
import directories as ani


def medianEnergy(infiles):

    # Establish path to analysis simulation location
    ani.setup_input_dirs(verbose=False)

    evalues = [i for f in infiles for i in re.split('_',f) if 'GeV' in i]
    evalues = [re.split('-|GeV',i) for i in evalues]
    emin = float(evalues[0][0])
    emax = float(evalues[-1][1])

    # Syntax is a little confused - was written to work with many ebins
    medians, sigL, sigR, var = ebin_params(ani.sim_hist, [emin, emax])
    medians = 10**(medians+9)
    labels = []
    for m in medians:
        # Fun syntax rounds to two sig figs
        if m >= 1e15:
            labels += [f'{float(f"{m/1e15:.2g}"):g}PeV']
        elif m >= 1e12:
            labels += [f'{float(f"{m/1e12:.2g}"):g}TeV']

    return labels[0]



def SetupAbsThresholdColormap(amin, amax, threshold):
    """ Create a color map for "two-sided" thresholds.  Below the threshold,
        the map is a cool green-blue palette.  Between the lower and upper
        threshold, the map is gray-white-gray.  Above the upper threshold,
        the map is a warm red-yellow palette.
    """

    #t_min = amin if threshold>abs(amin) else -threshold
    #t_max = amax if threshold>amax else threshold

    x1 = (-threshold - amin) / (amax - amin)
    x3 = (amax - threshold) / (amax - amin)
    x2 = 1. - x1 - x3
    gvl = 0.5
    thrDict = {
        "red"    : ((0.0, 1.0, 0.5), (x1, 0.0, gvl), (x1 + 0.5*x2, 1.0, 1.0),
                    (x1 + x2, gvl, 0.7), (1.0, 1.0, 1.0)),
        "green"  : ((0.0, 1.0, 1.0), (x1, 0.0, gvl), (x1 + 0.5*x2, 1.0, 1.0),
                    (x1 + x2, gvl, 0.0), (1.0, 1.0, 1.0)),
        "blue"   : ((0.0, 1.0, 1.0), (x1, 0.7, gvl), (x1 + 0.5*x2, 1.0, 1.0),
                    (x1 + x2, gvl, 0.0), (1.0, 0.5, 1.0)) }
    return LinearSegmentedColormap("thresholdColormap", thrDict, 256)


def SetupColorBar(label=None, mmin=None, mmax=None, ticks=None, coord="C",
                    fontsize='large', projaxis=hp.projaxes.HpxMollweideAxes):
    """ Create the color bar for a HEALPix figure
    """
    fig = plt.figure(1)
    ax = [axis for axis in fig.get_axes() if type(axis) is projaxis][0]
    shrink = 0.7
    orientation = 'horizontal'
    if projaxis == hp.projaxes.HpxCartesianAxes:
        shrink = 0.65
        orientation = 'vertical'
    #    pad = 0.03
    if projaxis == hp.projaxes.HpxOrthographicAxes:
        shrink = 0.6

    cb = fig.colorbar(ax.get_images()[0], ax=ax,
                orientation=orientation,
                shrink=shrink, aspect=50,
                pad=0.01, fraction=0.1,
                ticks=ticks,
                format=FormatStrFormatter("%g"))

    for l in cb.ax.get_xticklabels():
        l.set_fontsize(fontsize)

    ax0 = cb.ax.yaxis if orientation=='vertical' else cb.ax.xaxis
    tick_locs = ax0.get_ticklocs()
    tick_labels = [l.get_text() for l in ax0.get_ticklabels()]
    if float(tick_labels[0]) != float(mmin):
        tick_labels[0] = '%s' % mmin
        tick_locs[0] = 0
    if float(tick_labels[-1]) != float(mmax):
        tick_labels[-1] = '%s' % mmax
        tick_locs[-1] = 1
    diffs = [float(tick_labels[i+1]) - float(tick_labels[i]) for i in range(len(tick_labels) - 1)]
    if diffs[0] < diffs[1]/2.:
        tick_labels[1] = ''
    if diffs[-1] < diffs[-2]/2.:
        tick_labels[-2] = ''
    ax0.set_ticklabels(tick_labels)
    ax0.set_ticks(tick_locs)

    cb.set_label(label, size=fontsize)

    if projaxis == hp.projaxes.HpxMollweideAxes:
        if coord == "C":
            ax.annotate("0$^\circ$", xy=(1.8, -0.75), size=fontsize)
            ax.annotate("360$^\circ$", xy=(-1.99, -0.75), size=fontsize)
        else:
            ax.annotate("-180$^\circ$", xy=(1.65, 0.625), size=fontsize)
            ax.annotate("180$^\circ$", xy=(-1.9, 0.625), size=fontsize)


def makeTitle(args, options):
    files = [os.path.splitext(os.path.basename(f))[0] for f in args]
    params = np.transpose([f.split('_') for f in files])
    newparams = ['' for i in params]
    for i in range(len(params)):
        values = sorted(list(set(params[i])))
        if len(values) == 1:
            newparams[i] = values[0]
            continue
        if values[0][:2] in ['IC','IT']:
            newparams[i] = '-'.join(values)
        if 'GeV' in values[0]:
            evals = np.array([re.split('-|GeV', v) for v in values]).flatten()
            evals = sorted([j for j in evals if j != ''])
            eflts = [float(j) for j in evals]
            evals = [j for (k,j) in sorted(zip(eflts,evals))]
            newparams[i] = '%s-%sGeV' % (evals[0], evals[-1])
    title = ' '.join(newparams)
    title += ' %s %02ddeg' % (options.mapName, options.smooth)
    #title = title.replace('.', 'pt')
    if options.multi:
        title += ' l%ssub' % options.multi
    if options.polar:
        title += ' polar'
    if options.cmap != 'jet':
        title += ' %s' % options.cmap
    return title


if __name__ == "__main__":

    # Establish default output paths
    ani.setup_output_dirs(verbose=False)

    usage = 'Usage %prog [options] INPUT.[fits]'
    parser = OptionParser(usage)

    parser.add_option('-m', '--min', dest='min', type='string',
            help='Plot minimum value')
    parser.add_option('-M', '--max', dest='max', type='string',
            help='Plot maximum value')
    parser.add_option('-d', '--decmin', dest='decmin', type=float,
            default=-90., help='Minimum declination value (90->-90)')
    parser.add_option('-D', '--decmax', dest='decmax', type=float,
            default=90., help='Maximum declination value (90->-90)')
    parser.add_option('-r', '--ramin', dest='ramin', type=float,
            help='Minimum RA value')
    parser.add_option('-R', '--ramax', dest='ramax', type=float,
            help='Maximum RA value')
    parser.add_option('--mask', dest='mask', default=False, 
            action='store_true', help='Intelligent masking')

    parser.add_option('--saveFITS', dest='saveFITS', action='store_true',
            default=False, help='Save map as fits file')

    parser.add_option('-n', '--mapName', dest='mapName',
            help='Map type desired (sig, relint, relint_err, data, bg)')
    parser.add_option('-s', '--scale', dest='scale', type=float,
            help='Scale the map after input')
    parser.add_option('-S', '--smooth', dest='smooth', type=float, default=0,
            help='Desired smoothing radius (in degrees)')
    parser.add_option('--norm', dest='norm',
            default=False, action='store_true',
            help='Normalize the top-hat smoothing process')
    parser.add_option('--stype', dest='stype', default='tophat',
            help='Option for smoothing type [tophat|gauss]')
    parser.add_option('--swindow', dest='swindow', type=float, default=3,
            help='Option for smoothing window')
    parser.add_option('--multi', dest='multi', type=int,
            help='Use Multipole subtraction')
    parser.add_option('--fix_multi', dest='fix_multi',
            default=False, action='store_true',
            help='Fix multipole subtraction to values from cumulative map')

    parser.add_option('-x', '--threshold', dest='threshold', type=float,
            help='Threshold value for plotting data')
    parser.add_option('-c', '--coords', dest='coords', default='C',
            help='C=equatorial, G=galactic, E=ecliptic')
    parser.add_option('--gplane', dest='gplane',
            default=False, action='store_true',
            help='Show the galactic plane')
    parser.add_option('--half', action="store_true", dest='half',
            default=False, help='Show only bottom half of the sky')

    parser.add_option('--title', action="store_true", dest="title",
            default=False, help='Show the title on the plot')
    parser.add_option('--outDir', dest='outDir',
            default=ani.figs,
            help='Option for changing output directory')
    parser.add_option('--prelim', action='store_true', dest='prelim',
            default=False, help='Indicate plot is preliminary')
    parser.add_option('--llabel', dest='llabel',
            default=False, help='Optional left label overlay on map')
    parser.add_option('--rlabel', dest='rlabel',
            default=False, help='Optional right label overlay on map')
    parser.add_option('--polar', dest='polar',
            default=False, action='store_true',
            help='Polar gnomonic view of map')
    parser.add_option('--customOut', dest='customOut',
            help='Option for custom output file name')
    parser.add_option('--ext', dest='ext',
            default='png', help='Output file extension')
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
            default=False, help='Verbose output')
    parser.add_option('--cmap', default='jet',
            help='Colormap option')


    options, args = parser.parse_args()
    if len(args) < 1:
        parser.error('Incorrect number of arguments')

    if not options.mapName:
        options.mapName = raw_input('Choose map type [data|bg|sig|relint]: ')
        print()

    detector = os.path.basename(args[0])[:2]
    if options.mask:
        options.decmax = -25.
        if detector == 'IT':
            options.decmax = -35.
        options.mask = False    # Revisit: why is this necessary

    opts = vars(options).copy()
    m = getMap(args, **opts)

    # Multiply by scale
    if options.scale:
        m[m!=hp.UNSEEN] *= (10**options.scale)

    # Setup the coordinate system
    rot = 180
    if options.coords == 'G':
        options.coords = 'CG'
        rot = 0
    if options.coords == 'E':
        options.coords = 'CE'
        rot = 250

    # Labeling for energy-binned maps
    if not options.llabel and any(['GeV' in i for i in args]):
        options.llabel = medianEnergy(args)

    # Mollweide (default), polar, or Cartesian projection
    proj = 'Mollweide'
    projaxis = hp.projaxes.HpxMollweideAxes
    if options.polar:
        proj='Orthographic'
        projaxis = hp.projaxes.HpxOrthographicAxes
    # Useful for square, zoomed-in segments
    if options.ramin!=None and options.ramax!=None:
        proj = 'Cartesian'
        projaxis = hp.projaxes.HpxCartesianAxes

    # Find min and max for unmasked pixels
    unmasked = np.array([i for i in m if (i!=hp.UNSEEN and i!=np.inf)])
    mmin = float(options.min) if options.min else unmasked.min()
    mmax = float(options.max) if options.max else unmasked.max()
    # In the case of a threshold outside of our range, set range to threshold
    if options.threshold:
        mmin = -options.threshold if mmin > -options.threshold else mmin
        mmax = options.threshold if mmax < options.threshold else mmax
    if not options.min:
        options.min = '%.2f' % mmin
    if not options.max:
        options.max = '%.2f' % mmax

    # Setup colormap with option for threshold
    colormap = plt.get_cmap(options.cmap)
    if options.threshold:
        colormap = SetupAbsThresholdColormap(mmin, mmax, options.threshold)
    colormap.set_under('white')
    colormap.set_bad('gray')

    # General plot parameter setup
    fig = plt.figure(1)
    fontsize = 'small' if proj!='Cartesian' else medium
    title = makeTitle(args, options)    # Automatically generated title
    pltParams = {'fig':1, 'rot':rot, 'title':title, 'min':mmin, 'max':mmax, \
            'cbar':False, 'notext':True, 'coord':options.coords, \
            'cmap':colormap}

    # Create the plot
    if proj == 'Cartesian':
        lonra = [options.ramin, options.ramax]
        latra = [options.decmin, options.decmax]
        hp.cartview(m, lonra=lonra, latra=latra, **pltParams)
        ax = fig.axes[0]
        ax.axis('on')
        ax.set_xlabel(r'Right Ascension [$^{\circ}$]')
        ax.set_ylabel(r'Declination [$^{\circ}$]')
        xlabels = ['%i' % (rot-xtick) for xtick in ax.get_xticks()]
        ax.set_xticklabels(xlabels)
    elif proj == 'Orthographic':
        pltParams['rot'] = [0,-90,rot]
        hp.orthview(m, half_sky=True, **pltParams)
    else:
        hp.mollview(m, **pltParams)
    # Graticule throws a RuntimeWarning with graticule in polar plots?
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        hp.graticule(verbose=False, lw=0.5)

    # Show galactic plane
    # NOTE: functionality doesn't work with polar projection?
    if options.gplane:
        theta = np.pi/2 * np.ones(100)
        phi = np.arange(0, 360, 3.6) * np.pi/180.
        hp.projplot(theta, phi, 'k--', coord='G', lw=0.75)
        hp.projplot(np.pi/2, 0, 'k^', coord='G', ms=5)

    # Set up the color bar
    labelDict = {'relint':'Relative Intensity'}
    labelDict.update({'sig':'Significance [$\sigma$]'})
    labelDict.update({'data':'Data','bg':'Background'})
    labelDict.update({'relint_err':'Relative Intensity Error'})
    labelDict.update({'fit':'Multipole Fit (Relative Intensity)'})
    label = labelDict[options.mapName]
    if options.scale:
        label += ' [x 10$^{-%d}$]' % options.scale
    cbarParams = {'label':label, 'mmin':options.min, 'mmax':options.max, \
            'coord':options.coords, 'fontsize':fontsize, 'projaxis':projaxis}
    SetupColorBar(**cbarParams)

    # Options for half size map and labels
    w, h = fig.get_size_inches()
    lParams = {'size':'large','color':'white','family':'sans-serif'}
    ax = [axis for axis in fig.get_axes() if type(axis) is projaxis][0]
    if options.polar:
        lParams['color'] = 'black'
        if options.llabel:
            lbl = '%s %s' % (options.llabel[:-3], options.llabel[-3:])
            ax.annotate(lbl, xy=(-1,.9), **lParams)
        if options.rlabel:
            ax.annotate(options.rlabel, xy=(.6,.9), **lParams)
    if not options.title:
        ax.set_title(title, visible=False)
    if options.half and options.polar:
        print('half is somehow true?')
    if options.half:
        ax.set_ylim(-1, 0.005)
        if options.llabel:
            lbl = '%s %s' % (options.llabel[:-3], options.llabel[-3:])
            ax.annotate(lbl, xy=(-1.85,-0.24), **lParams)
        if options.rlabel:
            ax.annotate(options.rlabel, xy=(1.3,-0.24), **lParams)
        fig.set_size_inches(w, h/2.8, forward=True)
    if options.prelim:
        ax = [axis for axis in fig.get_axes() if type(axis) is projaxis][0]
        IT = 'IceTop' if detector=='IT' else 'IceCube'
        ax.annotate(IT+' Preliminary', xy=(0.2,-0.24), **lParams)

    outFile  = '%s/%s' % (options.outDir, title.replace(' ', '_'))
    #print('Outfile: {}'.format(outFile))
    if options.customOut:
        outFile = '%s/%s' % (options.outDir, options.customOut)
    plt.savefig(outFile+'.'+options.ext, dpi=300, bbox_inches='tight')
    if options.saveFITS:
        hp.fitsfunc.write_map(outFile+'.fits', m)


