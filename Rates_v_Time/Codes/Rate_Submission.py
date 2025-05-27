from glob import glob 
import healpy as hp 
import argparse 
import os


if __name__ == "__main__": 
    p=argparse.ArgumentParser()
   
    p.add_argument( "--choose", dest='choose',
    nargs='+',
    help ="chooses configuration year")
    args = p.parse_args()

    if args.choose:
        
        for choose in args.choose:

            file_Z = "/data/user/zhardnett/anisotropy/new_maps/IC86-"f'{choose}'
            file_M = "/data/user/fmcnally/anisotropy/maps/IC86-"f'{choose}'
            config_filez= glob(f"{file_Z}/{f'IC86-{choose}_24H_sid_????-??-??.fits'}")
            config_filem= glob(f"{file_M}/{f'IC86-{choose}_24H_sid_????-??-??.fits'}")

            config_filem.sort()
            config_filez.sort()

            n_z= len(config_filez)
            n_f= len(config_filem)
            counts1=0
            counts2=0

            print("Working on McNally's file")
            for i, m in enumerate(config_filem):
                print(f'Adding file {i} of {n_f}')
                a = hp.read_map(m, verbose=False)
                counts1+= a.sum()

            print("Working on Zoë's file")
            for i, z in enumerate(config_filez): 
                print(f'Adding file {i} of {n_z}')
                b = hp.read_map(z, verbose=False)
                counts2+= b.sum()
               

            if counts1 != counts2:
                print("The rates are different! :)")
                print("Zoë's rates:")
                print(counts2)
                print("McNally's rates:")
                print(counts1)
            else:
                print("The rates are the same!! :o")
                print("Zoë's rates:")
                print(counts2)
                print("McNally's rates:")
                print(counts1)

        
