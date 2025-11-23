#!/usr/bin/env python
# summing the total number of events per calendar year for IceTop

import argparse
import json
import os
from datetime import datetime

if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description='Calculate event counts from IceTop fits files (June 1 to May 31)')
    p.add_argument('-t', '--tier', dest='tier',
                   type=int, nargs='+',
                   default=[1, 2, 3, 4],
                   help='Energy tier to run over')
    p.add_argument('-y', '--year', dest='year',
                   type=int, nargs='+',
                   default=list(range(2011, 2022)),
                   help='Starting year (June 1)')
    args = p.parse_args()

    prefix = "/data/user/cjoiner/icetop_12yr/stability/counts_"

    for year in args.year:
        next_year = year + 1
        yearly_total = 0
        print(f"Year {year}:")

        for tier in args.tier:
            filename1 = f"{prefix}{year}_Tier{tier}.json"
            filename2 = f"{prefix}{next_year}_Tier{tier}.json"

            # Load may 13 - dec 31
            if os.path.isfile(filename1):
                with open(filename1, 'r') as f:
                    data = json.load(f)
                tier_sum1 = sum(
                    count for date, count in data.items()
                    if datetime.strptime(date, "%Y-%m-%d").date() >= datetime(year, 5, 13).date()
                )
            else:
                tier_sum1 = 0

            # Load jan 1 - may 12
            if os.path.isfile(filename2):
                with open(filename2, 'r') as f:
                    data = json.load(f)
                tier_sum2 = sum(
                    count for date, count in data.items()
                    if datetime.strptime(date, "%Y-%m-%d").date() <= datetime(next_year, 5, 12).date()
                )
            else:
                tier_sum2 = 0

            tier_total = tier_sum1 + tier_sum2
            yearly_total += tier_total

            print(f"  Tier {tier}: {tier_total}")

        print(f"  Total: {yearly_total}\n")
