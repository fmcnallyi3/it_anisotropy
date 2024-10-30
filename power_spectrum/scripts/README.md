This directory contains:

- README.md : This file
- aps.py : generates and plots the angular power spectrum
- aps_ve.py : visualization of select multipole moments as a function of energy
- isoErr.py : generates the isotropic bands
- maker.py : wrapper script for creation of error bars or power spectra
- statErr.py : generates the statistical error bars
- sysErr.py : generates the systematic error bars

Instructions:

- Use maker.py to generate all uncertainties for both the all-data and the energy-split maps
- Production of the desired power spectra can be done using plotMaker.py (at the
  parent level) or aps.py | aps_ve.py

Additional notes: these scripts are capable of combining data (useful for
merging energy bins) and plotting power spectra from various maps against each
other. Using the argument "-f [map1] [map2]" will calculate the power spectra
for the combined maps. Using the argument "-f [map1] -f [map2]" will show the
two power spectra for the individual maps. The same approach applies to the
--syserr and --staterr flags within aps.py
