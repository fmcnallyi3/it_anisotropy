#!/bin/bash
date
hostname

/home/cjoiner/it_anisotropy/stability/count_finder.py -f /data/ana/CosmicRay/Anisotropy/IceTop/ITpass2/output/sidereal_unblinded/tier1/fitsbydate/2015 -o /data/user/cjoiner/icetop_12yr/stability/counts_2015_Tier1.json

date
echo 'Fin'
