This is the directory for the creation of daily and merged fits files, using
the time scrambling method to produce background maps.

Code was compiled with Juan Carlos' py2-v1 cvmfs project 
(${CVMFS}/users/juancarlos/tools/py2-v1/setup.sh) 
and an old installation of offline software 
(/data/user/fmcnally/offline/V04-08-00/build/env-shell.sh).
Both are hard-coded into the submission script (maker.py)


It includes:

- README.md : this file

- Makefile : compile time scrambling code

- TimeScramble.cc : create and save data and background maps

- SimpleDST : ROOT classes for accessing SimpleDST and
  trigger event information

- maker.py : wrapper script for cluster submission of TimeScramble

