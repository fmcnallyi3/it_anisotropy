#!/bin/bash
date
hostname

/home/cjoiner/it_anisotropy/stability/count_finder.py -f /data/ana/CosmicRay/Anisotropy/IceTop/ITpass2/output/sidereal_unblinded/tier3/fitsbydate/2016 -o /data/user/cjoiner/icetop_12yr/stability/counts_2016_Tier3.json

date
echo 'Fin'
