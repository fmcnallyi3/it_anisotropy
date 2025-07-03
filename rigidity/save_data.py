import os, sys, glob, tables, argparse
import numpy as np
# pip install simweights <--- run this once to install the package
# then replace <username> with your username and <version> with your Python version
sys.path.append('/home/tfutrell/.local/lib/python3.12/site-packages')
import simweights

def main(args):
    dir_base = f'/data/ana/CosmicRay/IceTop_level3/sim/IC86.{args.year}/{args.model}/'
    dir_end = '/h5files/*.h5'

    if args.year == 2012:
        if args.model == 'EPOS-LHC':
            fe_list = glob.glob(dir_base + 'Fe/12635_v1s' + dir_end)
            he_list = None
            o_list = None
            p_list = glob.glob(dir_base + 'p/12634_v1s' + dir_end)
        
        elif args.model == 'SIBYLL2.1':
            fe_list = glob.glob(dir_base + 'Fe/12362_v1s' + dir_end) # Can be combined with 20144_v1s
            he_list = glob.glob(dir_base + 'He/12630_v1s' + dir_end) # Can be combined with 20145_v1s
            o_list = glob.glob(dir_base + 'O/12631_v1s' + dir_end) # Can be combined with 20146_v1s
            p_list = glob.glob(dir_base + 'p/12360_v1s' + dir_end) # Can be combined with 20143_v1s
        
        elif args.model == 'SIBYLL2.3':            
            fe_list = glob.glob(dir_base + 'Fe/12633_v1s' + dir_end)
            he_list = None
            o_list = None
            p_list = glob.glob(dir_base + 'p/12632_v1s' + dir_end)

    elif args.year == 2015:    
        fe_list = glob.glob(dir_base + 'Fe/20180_v1s' + dir_end)
        he_list = glob.glob(dir_base + 'He/20178_v1s' + dir_end)
        o_list = glob.glob(dir_base + 'O/20179_v1s' + dir_end)
        p_list = glob.glob(dir_base + 'p/20174_v1s' + dir_end)

    elif args.year == 2018:
        if args.model == 'EPOS-LHC':
            # Missing IceTopHLCSeedRTPulses_SnowUnAttenuated_info in Fe/23201_v3/h5files/...5.0
            fe_list = []
            he_list = []
            o_list = []
            p_list = []
            for i in range(51, 69):
                fe_list += glob.glob(dir_base + 'Fe/23201_v3' + f'/h5files/*E{i/10}*.h5')
                he_list += glob.glob(dir_base + 'He/23199_v3' + f'/h5files/*E{i/10}*.h5')
                o_list += glob.glob(dir_base + 'O/23200_v3' + f'/h5files/*E{i/10}*.h5')
                p_list += glob.glob(dir_base + 'p/23198_v3' + f'/h5files/*E{i/10}*.h5')
        
        elif args.model == 'SIBYLL2.3d':
            fe_list = []
            he_list = []
            o_list = []
            p_list = []
            for i in range(48, 79):
                fe_list = glob.glob(dir_base + 'Fe_allE_links_v3' + f'/h5files/*E{i/10}*.h5')
                he_list = glob.glob(dir_base + 'He_allE_links_v3' + f'/h5files/*E{i/10}*.h5')
                o_list = glob.glob(dir_base + 'O_allE_links_v3' + f'/h5files/*E{i/10}*.h5')
                p_list = glob.glob(dir_base + 'p_allE_links_v3' + f'/h5files/*E{i/10}*.h5')

    weighter = None
    print('Getting iron weights...')

    for filename in fe_list:
        file_obj = tables.open_file(filename, 'r')
        
        if weighter is None:
            weighter = simweights.IceTopWeighter(file_obj)
        else:
            weighter += simweights.IceTopWeighter(file_obj)

    print('Got iron weights!')

    if not he_list == None:
        print('Getting helium weights...')

        for filename in he_list:
            file_obj = tables.open_file(filename, 'r')
            weighter += simweights.IceTopWeighter(file_obj)

        print('Got helium weights!')

    if not o_list == None:
        print('Getting oxygen weights...')
            
            
        for filename in o_list:
            file_obj = tables.open_file(filename, 'r')
            weighter += simweights.IceTopWeighter(file_obj)

        print('Got oxygen weights!')

    print('Getting proton weights...')

    for filename in p_list:
        file_obj = tables.open_file(filename, 'r')
        weighter += simweights.IceTopWeighter(file_obj)

    print('Got proton weights!')

    # If the file path does not exist, create it
    if not os.path.exists(f'saved_data/{args.year}/{args.model}'):
        os.makedirs(f'saved_data/{args.year}/{args.model}/')

    # Save energy
    if not os.path.isfile(f'saved_data/{args.year}/{args.model}/energy.npy'):
        print('Saving energy...')
        with open(f'saved_data/{args.year}/{args.model}/energy.npy', 'wb') as f:
            np.save(f, weighter.get_column('MCPrimary', 'energy'))
        print('Saved!')
    else:
        print('File already exists, skipping')

    # Save particle type
    if not os.path.isfile(f'saved_data/{args.year}/{args.model}/particle_type.npy'):
        print('Saving particle type...')
        with open(f'saved_data/{args.year}/{args.model}/particle_type.npy', 'wb') as f:
            np.save(f, weighter.get_column('MCPrimary', 'type'))
        print('Saved!')
    else:
        print('File already exists, skipping')

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

    # Save hits
    if not os.path.isfile(f'saved_data/{args.year}/{args.model}/hits.npy'):
        print('Saving hits...')
        with open(f'saved_data/{args.year}/{args.model}/hits.npy', 'wb') as f:
            np.save(f, weighter.get_column('IceTopHLCSeedRTPulses_SnowUnAttenuated_info', 'nstrings').astype(int))
        print('Saved!')
    else:
        print('File already exists, skipping')

    # Save reconstruction passed cut
    if not os.path.isfile(f'saved_data/{args.year}/{args.model}/reco_pass.npy'):
        print('Saving reco_pass...')
        with open(f'saved_data/{args.year}/{args.model}/reco_pass.npy', 'wb') as f:
            np.save(f, weighter.get_column('IT73AnalysisIceTopQualityCuts', 'IceTop_reco_succeeded').astype(bool))
        print('Saved!')
    else:
        print('File already exists, skipping')

    # Save zenith cut
    if not os.path.isfile(f'saved_data/{args.year}/{args.model}/zenith_cut.npy'):
        print('Saving zenith cut...')
        with open(f'saved_data/{args.year}/{args.model}/zenith_cut.npy', 'wb') as f:
            np.save(f, weighter.get_column('MCPrimary', 'zenith') < np.radians(55))
        print('Saved!')
    else:
        print('File already exists, skipping')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Save data to a .npy file")

    parser.add_argument('-y', '--year', type=int, required=True, help='2012, 2015, 2018')
    parser.add_argument('-m', '--model', type=str, required=True, help='(Depending on year) EPOS-LHC, SIBYLL2.1, SIBYLL2.3, SIBYLL2.3d')

    args = parser.parse_args()
    
    main(args)