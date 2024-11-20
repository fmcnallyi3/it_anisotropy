<p align= "center"> Welcome to the Rates Readme!!! </p> 

  ## Goals: To plot the rates of events measured during a configuration (From IceTop's Data)
### Operation 
- Copy stability tools from McNally to this folder
- Need an updated Good Run List
- Test the stability tools on a small data sample
  - ROOT file processing
  - FITS file processing
  - Visualization
      - **Add Example Graph?** 
- Process all the data

## List of Codes
In order to achevie goal, running these codes are required. The follwing codes are shown below:
- fits_extractor.py  
- fits_merge.py  
- root_merge.py  
- root_submitter.py 
- root_extractor
## Code Functions 
**fits_extractor** : \

**fits_merge** : \

**root_merge** : 
- Merges daily root summaries by detector configuration
- Currently uses versions extracted by eschmidt (May need to update)
  
**root_submitter**: 
- Submits root files to the cluster in ~daily batches for one detector year
  
**root_extractor** :
  - Opens a collection of root files (meant to be ~1 day) and
    - Calculates the number of events and livetime for each run
 - Stores as [date - run - nevents - livetime] in a .txt file
   
**rate_finder.py** :
 - Creates summary text files and stores rate information for each detector
   configuration
Here is the list of requirements for 'rate_finder':
    - Find the location of good run list output from i3live
    - Find the location of fits summary text files
       - Will generate automatically if maps have been updated
    - Find the location of root summary text files from root_extractor.py
       - To be submitted by root_submitter.py then merged by root_merge.py
**rate_check.py** :
 - Generates rate plots for rates from root or fits files using summary output
   from rate_finder.py
 - Optionally outputs bad days using rolling average (from eschmidt)


