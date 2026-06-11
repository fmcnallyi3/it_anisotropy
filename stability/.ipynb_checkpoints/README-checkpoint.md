This is an incomplete set of tools, designed to begin the rate vs time analysis
for the 12-year IceTop anisotropy paper. It currently features the following
items:

- `README.md` : This file
- `count_finder.py` : Calculates daily counts from map files located in Alex
  McClure's output directory in /data/ana
- `directories.py` : Designed to establish names for commonly-used directories
  (location of daily maps, output destination for rate plots, etc.). INCOMPLETE
-- has not been updated since its original use with IceCube
- `grl_tools.py` : Tools for reading the good run lists from Serap and I3Live
- `livetime_test.ipynb` : Jupyter notebook for playing with livetime and rate
  calculations
- `maker.py` : Submission script for count_finder.py
- `rate_finder.py` : Designed to calculate rate on a daily basis. INCOMPLETE --
  has not been updated since its original use with IceCube
- `rate_check.py` : Designed to look for significant deviations from a rolling
  average rate. INCOMPLETE -- has not been updated since its original use with
IceCube
- `submitter` : Directory with cluster submission tools


To-Do items for CJ:
- `directories.py` : once the analysis paths are set for the IceTop analysis,
  update this script to point to them (and, at least temporarily, your own
/data/user for output) and incorporate them in place of absolute file paths in
other scripts (like maker.py)
- `rate_finder.py` : we are (at least initially) only interested in calculating
  the event rate using the maps for counts and i3live for livetime.
Move/comment out all unnecessary code and make it so this script does exactly
that.
- `rate_check.py` : make sure that this now runs with the output from your
  adapted rate_finder.py and show me some plots!
