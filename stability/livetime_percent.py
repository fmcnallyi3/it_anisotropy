import argparse
import os
from glob import glob
import grl_tools

if __name__ == "__main__":
    p = argparse.ArgumentParser(description='Calculate daily counts from IceTop fits files')
    p.add_argument('-y', '--year', dest='year',
            type=int, nargs='+',
            default=list(range(2011, 2022)),
            help='Calendar year(s) to process')
    args = p.parse_args()

    # Load Serap's icetop GRL files
    grl_base = '/data/ana/CosmicRay/IceTop_GRL'
    grl_files = sorted(glob(f'{grl_base}/IC86_20*.txt'))

    it_goodruns = []
    for grl_file in grl_files:
        it_goodruns += grl_tools.parse_seraps_GRL(grl_file)

    for year in args.year:
        next_year = year + 1
        start = f'{year}-05-13 00:00:00'
        end = f'{next_year}-05-13 00:00:00'

        # Determine number of seconds in the year (w/ leap year check)
        if year in [2011, 2015, 2019]:
            seconds = float(31622400)
        else:
            seconds = float(31536000)

        # Get i3live GRL for the period
        i3_goodruns = grl_tools.i3live_grl(start, end, icetop=True)

        # Calculate livetimes for IceTop
        i3_livetime = grl_tools.daily_livetime(i3_goodruns, it_goodruns)

        livetime_year = 0.0
        for day in i3_livetime:
            livetime_year += sum(i3_livetime[day].values())

        # Calculate livetime percentage
        i3_livetime_percent = (livetime_year / seconds) * 100
        print(f"Livetime percent for year {year} is {i3_livetime_percent:.2f}%")
