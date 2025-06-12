# Plan for Power Spectrum with IceTop
 * The general plan for this project is to create Angular Power Spectra plots for data gathered from IceTop. These plots should look similar (in form) to the plots present on the 12-year Anisotropy paper, depicting a function as energy for any given spherical harmonic mode (L value).

## --- Notes from FM --- ##
This folder is designed to tackle *one* task: the creation of angular power spectra for IceTop. With this idea in mind, please make the following changes:
- Set the isotropic error band script to run with n = 1e6 by default
- Set the statistical and systematic uncertainties to run with n = 1e5 by default
- Produce all uncertainties for every Tier
    - This task should be recorded in a way such that it is repeatable. I usually use something like `maker.py` to record the arguments used (input files, output files, n...) in cases like this
- Produce polished plots of the angular power spectra for each Tier
    - The above note also applies here
- Remove **all** excess code that is not related to one of the above objectives

## The following is the list of actions to accomplish the goals of this project.

* acquire and review code for power spectrum from in-ice data
* locate Ice Top data
* edit code where needed
* attempt running code on In-Ice data
  * trouble shoot until code works and replicates In-Ice results
* attempt running code on IceTop data
  *   trouble shoot until code works
* analyze product to check if plots are good
  *   compare IceTop plots with In Ice plots
  *   trouble shoot until good plots are made
* submit plots for review with McNally
  *   If plots are bad, trouble shoot for good plots

## General Course of Action
 * Collecting files
   *   pull power_spectrum files (use git pull, or git pull --rebase to ensure local changes do not get overwritten)
   *   Alternatively, for direct access to the files go to https://github.com/icecube/wg-cosmic-rays/tree/cr_anisotropy/analyses/IC86.2011-IC86.2021_CRAnisotropy
   *   IceTop data used is located in /data/ana/CosmicRay/IceTop_level3/exp/IC86.*_pass2_v0*/{year}/{date}/Run*/Level3_IC86.*Subrun*.i3.*
    *  stars fill in for digits in iteration.
 * Change files
   *    Run mapFunctions/directories.py to set up output directory pathways (current problems include: missing files from root location)
 * Running for Angular Power Spectrum (aps)
   *    before running any file, run cvmfs . Then run icetray .
    *   if you are returned a command not found error, then you may not have set up your cvmfs bash.  
   *    run plotMaker.py --powerspec to run the power spectrum portion of the code.
    *   Note: if files are "missing" invesitgate if pathways are set up with directories.py.
 * Checking if completed
   *   Go to /data/user/[your user]/anisotropy/figures_12yr to check for power spectrum graphs.
    *   use ls [the above pathway] to check.

## Scripts in This Folder

- plotMaker.py : wrapper script that can generate both the uncertainties and the angular power spectrum with simplified commands.
  - How to run: python [code] -f [input file path] -t t# -o [output file path] (recommended first run: -m to make the uncertainties.)
  - input and output file paths have set defualts, change these for your needs.
- aps.py : generates and plots the angular power spectrum
  - How to run: python [code] -f [input file path] -i [isoErr path] --staterr [statErr path] --syserr [sysErr path] -o [output file path] -l [label]
- isoErr.py : generates the isotropic bands
  - How to run: python [code] -f [input file path] -o [output file path] (optional: -n [int amount of times to run])
- statErr.py : generates the statistical error bars
  - How to run: python [code] -f [input file path] -o [output file path] (optiona: -n [int amount of times to run])
- sysErr.py : generates the systematic error bars
  - How to run: python [code] -f [input file path] -o [output file path] (optional: -n [int amount of times to run])
- map_functions.py: contains functions used in the above files for plot creation.

## Questions and Answers
* What to run for Angular Power Spectrum?
  * aps.py in scripts is what you want. Use -f [path to data] and -o [path to output] if you want a spectrum without noise bands and error bars. To inclue noise bands and error bars use the commands --sysErr [path to sysErr bars] --statErr [path to statErr bars] and -i [path to isotropic noise bands]
  * Use isoErr, statErr, and sysErr to produce noise bands and error bars. Use -f [path to data], -n [number of iterations], and -o [path to output].
* Where can I find the data?
  * /data/ana/CosmicRay/Anisotropy/IceTop/ITpass2/output/outpute/finalcombinedfits/. There are 4 energy bins. Run the code on the latest iteration of CR_IceTop_*.
  * If you cannot find the data, please ask!
