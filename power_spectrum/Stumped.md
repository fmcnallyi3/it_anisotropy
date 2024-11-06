# File to log problems that occur as they occur to record problems to be addressed.

- Aiden
  - Stumped: cloning the wg-cosmic-rays powerspec repo branch into it_anisotropy repo.
  - Current Idea: need proper SSH passkey for being able to access private repo from remote.
  - Solution: Ethan Dorr fixed it :D
  - Stumped: Locating data used in-ice. for future, unsure whether to use level 3 or level 4 ice top data.
  - Current Idea: use level 4 data and run code from wg-cosmic-rays repo.
  - Solution: use level 3 data. look at wiki for in-ice file.
  - Stumped: run command for aps.py, do not know what further commands the code wants.
  - Solution: run command with -h at the end.
  - Stumped: location of data files used by aps.py
  - Solution: run plotMaker.oy to find files from error message. (files found, but do not exist).
  - Notes for making uncertainty files:
    - ./maker.py --ebins --sys -n 10000
    - ./maker.py --ebins --stat -n 10000
    - ./maker.py --ebins --iso -n 100000
  - replace curly braces with true paths/values from directories and plotMaker to aps.py. run aps.py
- Ben
