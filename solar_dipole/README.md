# Welcome to the Solar Dipole "Read Me" File!

The `solar_dipole` folder is the repository for all things relating to IceTop and solar dipoles. Various tools can be found in this repository (tools are pending). Please use this file (or the ' #mercer ' slack channel and tag ' @mercer-ani ') to ask any questions or voice any concerns; it is checked at least weekly.

## SPRING 2025 Reflection and Outline for Future Steps 
### Reflection:
- thought
- thought 2
- thought 3
### Future Steps
- 

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
