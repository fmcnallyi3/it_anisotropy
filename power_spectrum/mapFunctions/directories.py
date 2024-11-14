#!/usr/bin/env python

##========================================================================##
## Creates a directory structure in your /data/user for output data       ##
##========================================================================##

import sys, os
import argparse


""" Paths to final data locations for input and internal project references """
def setup_input_dirs(verbose=True):

    current = os.path.dirname(os.path.realpath(__file__))

    # These paths should not change
    globalVals = globals().keys()
    global submitter, root, maps, cfg_maps, sim, sim_hist, aps
    submitter = '{}/submitter'.format(current)
    root = '/data/ana/CosmicRay/Anisotropy/IceCube'
    maps = '{}/twelve_year/maps/merged'.format(root)
    cfg_maps = '{}/twelve_year/maps'.format(root)
    sim = '/data/user/fmcnally/anisotropy/sim'
    sim_hist = '{}/IC86_20904_hist.npy'.format(sim)
    aps = '/data/user/fmcnally/anisotropy/powerspec'

    # Option to print changes to global variables
    if verbose:
        print('Newly accessible paths:')
        for key in globals().keys():
            if key not in globalVals:
                print('  %s = %s' % (key, globals()[key]))


""" Paths to local data locations for output (if rerunning analysis) """
def setup_output_dirs(user=None, verbose=True):

    current = os.path.dirname(os.path.realpath(__file__))

    if user is not None:
        with open(os.path.join(current,	"DirectoryUser.txt"), "w") as file:
            file.write(user)
    else:
       	if not os.path.isfile(os.path.join(current, "DirectoryUser.txt")):
       	    print("ERROR: directory paths have not been initialized. Please run directories.py --user <USER NAME>")
            exit()

        # Load user from file
        with open(os.path.join(current, "DirectoryUser.txt"), "r") as file:
            user = file.readline()

    # These paths can be changed if you want a different storage structure
    globalVals = globals().keys()
    global maps_out, sim_out, figs, aps_out
    maps_out = '/data/user/{}/anisotropy/maps'.format(user)
    sim_out = '/data/user/{}/anisotropy/sim'.format(user)
    figs    = '/data/user/{}/anisotropy/figures_12yr'.format(user)
    aps_out = '/data/user/{}/anisotropy/powerspec'.format(user)

    # Option to print changes to global variables
    if verbose:
        print('Newly accessible paths:')
        for key in globals().keys():
            if key not in globalVals:
                print('  %s = %s' % (key, globals()[key]))


if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Establishes paths for 12-year anisotropy analysis')
    p.add_argument('-u', '--user', dest='user',
            default=None,
            help='Username for path creation (ex: fmcnally)')
    args = p.parse_args()

    if args.user == None:
        print('Username required!')
        raise

    setup_input_dirs(verbose=False)
    setup_output_dirs(user=args.user, verbose=False)

    # Create desired directories for output (if they don't exist)
    for file_path in [maps_out, sim_out, figs, figs+"/annual", aps_out]:
        if os.path.exists(file_path):
            print('Path {} already exists. Skipping...'.format(file_path))
            continue
        os.makedirs(file_path)


