# Welcome to the Solar Dipole "Read Me" File!

The `solar_dipole` folder is the repository for all things relating to IceTop and solar dipoles. Various tools can be found in this repository (tools are pending). Please use this file (or the ' #mercer ' slack channel and tag ' @mercer-ani ') to ask any questions or voice any concerns; it is checked at least weekly.

## Spring 2025 Reflection and Outline for Future Steps 
### Reflection:
- This semester was more manuscript focused, so I didn't branch too much out on learning new JuptyerHub/GitHub techniques. I did not create the automated map-to-GIF code, but it was interesteing to implement it and learn how it worked!
- While researching for and writing the literature review, I genuinely enjoyed reading the DOM paper. For anyone that is doing more heavy lifting with analysis, that paper can provide some interesting insight (plus, that paper could even provide inspiration for a new project/focus for an incoming research student!)
- Again, peer meetings are only effective if at least one other person, although we obviously want everyone to go, is there to hold others accountable. For 75% of the peer meetings, it was just Aiden and I
### Future Steps
- Although I am sure Dr. McNally will guide and alter this project for the next student, I think a potential good (small) next step is to maybe produce all the maps (solar relint, sid relint, solar significance, sid significance, etc) with the gridded, half sky projection
- A bigger step is to create the 1D projections of these maps! I'm not sure what all is necessary to create these or how in-depth these graphs would be, but I'm sure some confidence interval or normal distribution curve could be created for these projections

## Fall 2025 Reflection and Outline for Future Steps 
### Reflection:
- I learned a lot about GitHub this semester. There was a small learning curve with learning how to properly pull, add, commit -m, and push my code but I feel confident in it now
      - I also learned about Git Token passwords and their importance
- I enjoyed helping Aylar with logging in with command prompt/jupyterhub/GitHub/cobalt for the first time because it challenged my basics and understanding of how everything connects. It is easy to forget all the shortcuts and things I have set up to make my code run properly
- Making weekly/bi-monthly goals are more useful than long-term goals
- Peer meetings are only effective if at least one other person is there to hold me accountable to go. I tend to struggle to be productive on my own unless it's the night before a research meeting
### Future Steps
- I want to be able to produce a "half map" (get rid of the blank, grey section)
- I need to write code that produces map(s) based on CALENDAR year instead of by DETECTOR year
- I need to write code that produces map(s) based on CALENDAR month instead of by DETECTOR month
- Regarding grid plotting...
  - WHAT is grid plotting?
  - WHY should I use grid plotting?
  - HOW to grid plot?
- Continue to refine my coding skills (regarding notation, better practice, vocabulary, and understanding)
  - ^ this is a good opportunity to set doable weekly goals for learning about programming
- Honors Manuscript due February 24th
  - ^ this is on my Bear Day content of 2024. Can be small updates and changes, but no major changes from that presentation to the manuscript

## Plan of Attack:
- Compile/read code by year and by month (11/13-11/27 ?)
      - see if `selectedMaps.ipynb` is good or not
- figure out how to print homogenous banded maps
      - why does it matter that I map sid signals and not solar signals?
      - is `AylarHelp.ipynb` correct? i don't think it is

## How to use Tool X:
1. instructions
2. 

## How to use Tool Y:
1. more instructions
2. 

## Questions/Concerns
- Ask question(s) here!

# How to move files:
## Installing Git: Helpful Links
- https://wiki.icecube.wisc.edu/index.php/Newbies#Programming_in_IceCube
- https://github.com/icecube/icecube.github.io/wiki/GitGuide%3AGitHub-in-IceCube
- https://github.com/fmcnallyi3/icetop-cnn/blob/main/README.md
- https://www.digitalocean.com/community/tutorials/how-to-contribute-to-open-source-getting-started-with-git
- https://git-scm.com/downloads/win

## How to get jupyterhub code into github:
### Go to command prompt:
- `ssh cobalt`
- `ls` this is just to see where I am
- `cd IceCube/` So when you clone the online repository, it’ll clone in this specific directory
## For first time set-up:
### When cloning repositories (McNally’s) and putting my own files (from JupyterHub) into the GitHub online repository, use:
- Clone using the “ <> Code “ button and copy the HTTPS link
- Paste this link into vscode after typing “` git clone `“. Should look something like:
    - `git clone https://github.com/fmcnallyi3/it_anisotropy.git`
- Now, we are going to copy all my python files from my IceCube directory into the it_anisotropy/solar_dipole folder
## To do this:
- `cp -r /home/srichie/IceCube/* /home/srichie/it_anisotropy/solar_dipole/`
    - `-r` means to include the contents of the folder
    - `*` is included to execute the function **get this checked**
- `ls #sanity check`
- `git pull`
- `git add .`
- `git status`
- `git commit -m “Adding my files from JupyterHub”`
- `git push`
## Using GIT (not first time set-up)
- Before doing your work (so when you log in),
- `git pull` ; this updates all the code so you're working with the most recently pushed changes
- Then, once you’ve made your changes to whatever files,
    - `git add [files]`
    - `git mv [file] [directory]`
    - `git rm [file]`
- For example, if you want to add/stage all the files in a folder/directory, you can do git add .
- You can also list files individually, like `git add file1.py file2.txt file3.jpeg`
- Optionally, you can check which files and changes you’ve added/staged to the commit using
  - `git status`
- Next, to group these changes together and add a message,
  - `git commit -m “Your custom message!”`
- The `-m` means “use message”, and it will use the next message that you type within quotation marks
- Finally, to sync back with the internet and the online repository,
  - `git push`
- If your code isn't pushing, read the section below and make sure your token is correct and that you actually did `commit -m` (step above)

## Code not Pushing?? Try this :)
- Create a new key
  - When create this new token, make a default (classic) one
  - When asked to about your "Scope Selection", ONLY select repo and save
  
 ### Extra, Useful Commands
 - `git mkdir [Name of Your New Directory]`
 - cd ..
