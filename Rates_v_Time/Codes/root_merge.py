#!/usr/bin/env python

import json
import re
from glob import glob
import directories as stab
from collections import defaultdict

if __name__ == "__main__":

    # Establish default project-specific paths
    stab.setup_dirs()

    # Storage structure: root_data[cfg][day][run][events|livetime]
    root_data = defaultdict(lambda: defaultdict(
                            lambda: defaultdict(
                            lambda: defaultdict(int))))

    # Collect summary files for individual days
    day_files = sorted(glob(f'{stab.root_out}/*.txt'))
    configs = sorted(set([re.findall('IC86-\d{4}',f)[0] for f in day_files]))

    for cfg in configs:

        print(f'Working on {cfg}...')

        cfg_files = [f for f in day_files if cfg in f]
        cfg_data = []

        for cfg_file in cfg_files:
            with open(cfg_file, 'r') as f:
                cfg_data += f.readlines()

        cfg_data = [line.strip().split(' - ') for line in cfg_data]

        for day, run, ct, t in cfg_data:
            root_data[cfg][day][run]['events'] += int(ct)
            root_data[cfg][day][run]['livetime'] += int(t)

        with open(f'{stab.data}/root_summary.json', 'w') as f:
            json.dump(root_data, f)
