#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py3-v4.1.1/icetray-start
#METAPROJECT icetray/stable
import healpy as hp
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

def multipoleratios(l):
    return 1/((2*l + 1)*(l + 2)*(l + 1) )


def renorm(alm):
    
    cls = hp.alm2cl(alm)
    lmax = len(cls)-1

    ahlers = multipoleratios(np.arange(len(cls)))
    r = np.sqrt(ahlers/cls)
    
    newalm = np.zeros_like(alm)
    for l in range(1,len(cls)):
        idx = hp.sphtfunc.Alm.getidx(lmax=lmax,l=l, m=np.arange(0,l+1))
        newalm[idx]=alm[idx]*r[l] 
         
    
    return newalm



    
def make_aps(ax, ri, label='',top=None,bottom=None,color='black',fmt='o'):
    yerr1 = None
    yerr2 = None
    cls = None
    ccl = None
    
    npix = ri.size
    nside = hp.npix2nside(npix)
    
    if top is not None:
        toppix = hp.ang2pix(nside,0,top,lonlat=True)
        ri[:toppix]=hp.UNSEEN
        
    if bottom is not None:
        bottompix = hp.ang2pix(nside,0,bottom,lonlat=True)
        ri[bottompix:]=hp.UNSEEN
    
    ccl = hp.anafast(ri,lmax=40)
    ell = range(len(ccl))
    
    watermark = ""
    marker_size=9


    ax.plot(ell[1:40], 
            ccl[1:40],fmt,
            label=label,color=color,markersize=marker_size)


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser(
            description='Make Toy MC aps')
    p.add_argument('-l', '--lmax', dest='lmax', type=int, default=30,
            help="maximum ell")
    p.add_argument('-n', '--nside', dest='nside', 
            type=int, default=32,
            help='Healpix nside value')
    p.add_argument('-o', '--out', dest='out',
            default=None,
            help="save figure to file")
    args = p.parse_args()


    ell = np.array(range(1,max(args.nside,40)))
    aps = multipoleratios(ell)
    randomap = hp.synfast(aps,args.nside) 
    alm = hp.map2alm(randomap, lmax=args.lmax)
    almn = renorm(alm)
    fakemap = hp.alm2map(almn,args.nside)

        
    fig = plt.figure(figsize=(12, 7))
    ax = plt.subplot(111)
                         
    watermark = ""
    plt.plot(ell, aps,label="$1/(2\ell + 1)(\ell + 2)(\ell + 1)$")         
    make_aps(ax,fakemap,label='Injected',color='black',fmt='.')
    make_aps(ax,fakemap,label='$(-25^\circ,-90\circ)$',top=-25,
    bottom=None,color='red',fmt='.')

                         
    ax.legend(loc='upper left', numpoints=1, fontsize=14)
    for item in (ax.get_xticklabels() + ax.get_yticklabels()):
            item.set_fontsize(20)
            
    plt.xlabel('$\ell$',fontsize=28); plt.ylabel('$\~c_\ell$',fontsize=36);

    ax.text(0.25*(0+40), 0.3*(7e-11+1e-5), watermark, alpha=0.3,ha= 'left',
    fontsize=26)

    ax.set_yscale("log")
    ax2 = ax.twiny()  # ax2 is responsible for "top" axis and "right" axis
    angle_ticks = [180,45,20,10,6]
    if args.lmax > 30:
        angle_ticks.append(180/args.lmax)
    angle_l_ticks = list(map(lambda x:180/x,angle_ticks ))
    ax2.set_xticks([1]+angle_l_ticks)
    angle_ticks_labels = list(map(lambda x:"%u$^\circ$"%x,angle_ticks ))
    ax2.set_xticklabels([""]+angle_ticks_labels, fontsize=17)
    ax.set_xlim(0, args.lmax)
    ax.set_ylim(1e-6, 1e2)
    ax.grid(True)
    fig.savefig(args.out, dpi=100)


    #Create inset plot with cl = delta_ij
    
    fig = plt.figure(figsize=(12, 7))
    ax = plt.subplot(111)
 

    pt_aps = np.zeros_like(ell)
    pt_aps[12] = 1.0
    pt_randomap = hp.synfast(pt_aps,32) 
    make_aps(ax,pt_randomap,label='Injected',fmt='-')
    for idec in range(5,150,40):
        make_aps(ax,pt_randomap,label='$({}^\circ,-90\circ)$'.format(90-idec),
                 color=None, fmt='--',top=90-idec)

    ax.set_yscale("log")
    ax.set_xlim(0, args.lmax)
    ax.set_ylim(1e-4, 5e0)
    ax.grid(True)

    ax2 = ax.twiny()  # ax2 is responsible for "top" axis and "right" axis
    ax2.set_xticks([1]+angle_l_ticks)
    ax2.set_xticklabels([""]+angle_ticks_labels, fontsize=17)

    ax.set_xlabel('$\ell$',fontsize=28); ax.set_ylabel('$\~c_\ell$',fontsize=36);
    for item in (ax.get_xticklabels() + ax.get_yticklabels()):
            item.set_fontsize(20)
    ax.legend(loc='upper right', numpoints=1, fontsize=14)

    suffix = args.out.split(".")[-1]
    fig.savefig(args.out.replace(f'.{suffix}',f'_delta.{suffix}'), dpi=100)
