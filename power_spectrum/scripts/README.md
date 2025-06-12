This directory contains:

- aps.py : generates and plots the angular power spectrum
  - How to run: python [code] -f [input file path] -i [isoErr path] --staterr [statErr path] --syserr [sysErr path] -o [output file path] -l [label]
- isoErr.py : generates the isotropic bands
  - How to run: python [code] -f [input file path] -o [output file path] (optional: -n [int amount of times to run])
- statErr.py : generates the statistical error bars
  - How to run: python [code] -f [input file path] -o [output file path] (optiona: -n [int amount of times to run])
- sysErr.py : generates the systematic error bars
  - How to run: python [code] -f [input file path] -o [output file path] (optional: -n [int amount of times to run])

Instructions:

- Production of the desired power spectra can be done using plotMaker.py (at the
  parent level) or aps.py | aps_ve.py

Additional notes: these scripts are capable of combining data (useful for
merging energy bins) and plotting power spectra from various maps against each
other. Using the argument "-f [map1] [map2]" will calculate the power spectra
for the combined maps. Using the argument "-f [map1] -f [map2]" will show the
two power spectra for the individual maps. The same approach applies to the
--syserr and --staterr flags within aps.py
