# Requires cvmfs
import os, sys, tables, argparse

from glob import glob

import numpy as np
# pip install simweights <--- run this once to install the package
# then replace <username> with your username and <version> with your Python version
sys.path.append('/home/tfutrell/.local/lib/python3.12/site-packages')
import simweights

def main(args):
    # Set up the base directory for the files
    dir_base = f'/data/ana/CosmicRay/IceTop_level3/sim/IC86.{args.year}/{args.model}/'
    dir_end = '/h5files/*.h5'

    # Match the year and simulation to a list of files - if-elif statements because default cvmfs does not support match-case statements
    # If you want to add a year or simulation, add an (el)if args.year == <year>: line, then if an args.model == <model>: line, and then
    # a line file_list = glob(<Fe_directory>) + glob(<He_directory>) + glob(<O_directory>) + glob(<p_directory>)
    if args.year == 2012:
        if args.model == 'EPOS-LHC':
            file_list = glob(dir_base + 'Fe/12635_v1s' + dir_end) + glob(dir_base + 'p/12634_v1s' + dir_end)
        
        elif args.model == 'SIBYLL2.1':
            file_list = glob(dir_base + 'Fe/12362_v1s' + dir_end) # Can be combined with 20144_v1s
            file_list += glob(dir_base + 'He/12630_v1s' + dir_end) # Can be combined with 20145_v1s
            file_list += glob(dir_base + 'O/12631_v1s' + dir_end) # Can be combined with 20146_v1s
            file_list += glob(dir_base + 'p/12360_v1s' + dir_end) # Can be combined with 20143_v1s
        
        elif args.model == 'SIBYLL2.3':            
            file_list = glob(dir_base + 'Fe/12633_v1s' + dir_end) + glob(dir_base + 'p/12632_v1s' + dir_end)
        
        else:
            # Error case: user inputs undefined model
            print('No data for that model. Add the directory for that model first!')

    elif args.year == 2015:    
        file_list = glob(dir_base + 'Fe/20180_v1s' + dir_end) + glob(dir_base + 'He/20178_v1s' + dir_end) + glob(dir_base + 'O/20179_v1s' + dir_end) + glob(dir_base + 'p/20174_v1s' + dir_end)

    # 2018 is a little quirky, so it needs to be treated differently
    elif args.year == 2018:
        # Files of energy decade less than 5.1 do not have necessary columns
        if args.model == 'EPOS-LHC':
            file_list = []
            for i in range(51, 69):
                file_list += glob(dir_base + 'Fe/23201_v3' + f'/h5files/*E{i/10}*.h5') + glob(dir_base + 'He/23199_v3' + f'/h5files/*E{i/10}*.h5') + glob(dir_base + 'O/23200_v3' + f'/h5files/*E{i/10}*.h5') + glob(dir_base + 'p/23198_v3' + f'/h5files/*E{i/10}*.h5')
        
        # Files of energy decade less than 4.8 do not have necessary columns
        elif args.model == 'SIBYLL2.3d':
            file_list = []
            for i in range(48, 79):
                file_list += glob(dir_base + 'Fe_allE_links_v3' + f'/h5files/*E{i/10}*.h5') + glob(dir_base + 'He_allE_links_v3' + f'/h5files/*E{i/10}*.h5') + glob(dir_base + 'O_allE_links_v3' + f'/h5files/*E{i/10}*.h5') + glob(dir_base + 'p_allE_links_v3' + f'/h5files/*E{i/10}*.h5')
        
        else:
            # Error case: user inputs undefined model
            print('No data for that model. Add the directory for that model first!')

    else:
        # Error case: user inputs undefined year
        print('No data for that year. Add the directory for that year and model first!')

    # Set up the weighter
    weighter = None
    print('Getting weights, this can take up to two hours...')

    # Loop through every single file and load the weights for it
    # This is the longest, most resource-intensive part of the process
    for filename in file_list:
        file_obj = tables.open_file(filename, 'r')
        
        if weighter is None:
            weighter = simweights.IceTopWeighter(file_obj)
        else:
            weighter += simweights.IceTopWeighter(file_obj)

    print('Got weights!')

    # If the file path for the year and simulation does not exist, create it
    if not os.path.exists(f'saved_data/{args.year}/{args.model}'):
        os.makedirs(f'saved_data/{args.year}/{args.model}/')

    # Set up a dictionary for harvesting data - weights are harvested seperately
    # If you need more data, add it here
    DATA = {
        'MCPrimary': ['energy', 'type', 'zenith'],
        'IceTopHLCSeedRTPulses_SnowUnAttenuated_info': ['nstrings'],
        'IT73AnalysisIceTopQualityCuts': ['IceTop_reco_succeeded']
    }
    
    # Save data from DATA
    for row, sets in DATA.items():
        for column in sets:
            if not os.path.isfile(f'saved_data/{args.year}/{args.model}/{column}.npy'):
                print(f'Saving {column}')
                with open(f'saved_data/{args.year}/{args.model}/{column}.npy', 'wb') as f:
                    np.save(f, weighter.get_column(row, column))

                print('Saved!')

    # Save H4a weights
    if not os.path.isfile(f'saved_data/{args.year}/{args.model}/Hweights.npy'):
        print('Saving H4a weights...')
        with open(f'saved_data/{args.year}/{args.model}/Hweights.npy', 'wb') as f:
            np.save(f, weighter.get_weights(simweights.GaisserH4a_IT()))
        print('Saved!')
    else:
        print('File already exists, skipping')

    # Save GSF weights
    if not os.path.isfile(f'saved_data/{args.year}/{args.model}/Gweights.npy'):
        print('Saving GSF weights...')
        with open(f'saved_data/{args.year}/{args.model}/Gweights.npy', 'wb') as f:
            np.save(f, weighter.get_weights(simweights.GlobalSplineFit_IT()))
        print('Saved!')
    else:
        print('File already exists, skipping')
    
    # Close the weighter and finish up
    file_obj.close()
    print('Finished!')

if __name__ == '__main__':
    # Define the arguments for the file
    parser = argparse.ArgumentParser(description="Save data to a .npy file")

    # Include notes about available years and models here
    parser.add_argument('-y', '--year', type=int, required=True, help='2012, 2015, 2018')
    parser.add_argument('-m', '--model', type=str, required=True, help='(Depending on year) EPOS-LHC, SIBYLL2.1, SIBYLL2.3, SIBYLL2.3d')

    args = parser.parse_args()
    
    main(args)