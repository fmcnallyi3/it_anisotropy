#!/bin/bash
date
hostname

/home/cjoiner/it_anisotropy/stability/count_finder.py -f /data/ana/CosmicRay/Anisotropy/IceTop/ITpass2/output/sidereal_unblinded/tier2/fitsbydate/2014 -o /data/user/cjoiner/icetop_12yr/stability/counts_2014_Tier2.json

date
echo 'Fin'
