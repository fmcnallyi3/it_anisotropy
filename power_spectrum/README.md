# Plan for Power Spectrum with IceTop
 * The general plan for this project is to create Angular Power Spectra plots for data gathered from IceTop. These plots should look similar (in form) to the plots present on the 12-year Anisotropy paper, depicting a function as energy for any given spherical harmonic mode (L value).

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

## Questions and Answers
### Q/A section to record possible FAQs that may arrise. 
