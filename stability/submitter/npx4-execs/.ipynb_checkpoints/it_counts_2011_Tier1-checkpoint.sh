#!/bin/bash
date
hostname

/home/cjoiner/it_anisotropy/stability/count_finder.py -f /data/ana/CosmicRay/Anisotropy/IceTop/ITpass2/output/outpute/solar/tier1/ITpass2/2011 -o /data/user/cjoiner/icetop_12yr/stability/outpute_solar_counts_2011_Tier1.json

date
echo 'Fin'
