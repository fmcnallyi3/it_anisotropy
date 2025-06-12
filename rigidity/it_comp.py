#!/usr/bin/env python

import numpy as np
import h5py
import tables

from glob import glob
import simweights

if __name__ == "__main__":

    # Collect simulation files
    #dir = '/data/ana/CosmicRay/Anisotropy/IceTop/ITpass2/output/outputg/sim_try'
    # Note: this is an early point of uncertainty. I don't know if these are
    # really the right simulation files to be looking at. You'll need to check
    # this with the Loyola crew

    f_dir = '/data/user/rchapagain/cra_analysis/sim_2012_simweights'
    files = sorted(glob(f'{f_dir}/*.hdf5'))
    print(files)

    # Establish the assumed composition weighting scheme
    flux = simweights.GaisserH4a_IT()

    # I'm just going to look at the first simulation file
    # You will need to expand this to look at different files / combinations
    my_file = files[0]

    """ Bonus note: the 'with' command below is a cool way to read files, as it
    automatically closes the file once the loop is exited (good practice) """

    # Extract n_stations for each event --- needed to determine Tier
    print('Reading n_stations from file...')
    with h5py.File(my_file, 'r') as f:
        n_stations = np.array(f['NStations']['value'])

    print('Calculating sim weights from file...')
    with tables.open_file(my_file, 'r') as f:
        weighter = simweights.IceTopWeighter(f)
        weights = weighter.get_weights(flux)

    # Remove NaN's and infinities
    weights[np.isinf(weights)] = 0
    weights[np.isnan(weights)] = 0

    print(n_stations[:100])
    print(weights[:100])


    # You should now have an array of the weights for each event ("weights") 
    # and the number of stations hit in that event so you can classify what 
    # Tier the event fell in. 
