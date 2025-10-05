#!/usr/bin/env python
# summing the total number of events per calendar year for IceTop
import argparse
import json
import re
import numpy as np
import healpy as hp
import os

from glob import glob
from collections import defaultdict

if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description='Calculate daily counts from IceTop fits files')
    p.add_argument('-t', '--tier', dest='tier',
            type=int, nargs='+',
            default=[1,2,3,4],
            help='Energy tier to run over')
    p.add_argument('-y', '--year', dest='year',
            type=int, nargs='+',
            default=list(range(2011,2023)),
            help='Calendar year to process')
    args = p.parse_args()

    prefix = "/data/user/cjoiner/icetop_12yr/stability/counts_"
    for year in args.year:
        yearly_total = 0
        file_base = f'{prefix}{year}'
        for tier in args.tier:
            filename = f"{file_base}_Tier{tier}.json"
            if not os.path.isfile(filename):
                # print(f"Warning: File not found: {filename}")
                continue
            with open(f'{filename}', 'r') as f:
                data = json.load(f)
            tier_sum = sum(data.values())
            yearly_total += tier_sum
            #print(f"  Tier {tier}: {tier_sum}")

        print(f"Total for {year} (all tiers): {yearly_total}")