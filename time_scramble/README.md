# time_scramble

This is the directory for the creation of daily and merged fits files, using
the time scrambling method to produce background maps.

Code currently designed to be compiled with Juan Carlos' py2-v1 cvmfs project (/cvmfs/icecube.opensciencegrid.org/users/juancarlos/tools/py2-v1/setup.sh) and an old installation of offline software (/data/user/fmcnally/offline/V04-08-00/build/env-shell.sh). Both are hard-coded into the submission script (maker.py)

## Files

`Makefile`
- Instructions for C++ compilation

`maker.py`
- Wrapper script for cluster submission of TimeScramble

`merger.py`
- Merge daily output files into annual skymaps

`pysubmit.py`
- Job submission to cluster

`README.md`
- This file

`SimpleDST`
- ROOT classes for accessing SimpleDST and trigger event information

`TimeScramble.cc`
- Create and save data and time-scrambled background maps

`TS-Tester.ipynb`
- Jupyter notebook for comparison of time-scrambling and direct integration
