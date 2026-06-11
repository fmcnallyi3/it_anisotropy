#!/bin/bash
date
hostname

/home/cjoiner/it_anisotropy/stability/count_finder.py -f /data/ana/CosmicRay/Anisotropy/IceTop/ITpass2/output/sidereal_unblinded/tier4/fitsbydate/2022 -o /data/user/cjoiner/icetop_12yr/stability/counts_2022_Tier4.json

date
echo 'Fin'
