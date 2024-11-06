# Welcome to the Solar Dipole "Read Me" File!

The `solar_dipole` folder is the repository for all things relating to IceTop and solar dipoles. Various tools can be found in this repository (tools are pending). Please use this file (or the ' #mercer ' slack channel and tag ' @anisotropy ') to ask any questions or voice any concerns; it is checked at least weekly.

## How to use Tool X:
1. instructions
2. 

## How to use Took Y:
1. more instructions
2. 

## Plan of Attack:
- Rewrite yearly/monthly codes to where they're written with "better practice"
    - figure out why i can't push my betterpractice code
    - figure out why May 2019 is not working
 
- to figure out why i can't push my betterpractice code:
      - move my code safely somewhere, destroy the existing it_anisotropy file that i have (because I may have made a bad personal access token), and redo my cloning/my access to it_anisotropy??
- also follow my plan of attack in google doc

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
- For example, if you want to add/stage all the files in a folder/directory, you can do git add .
- You can also list files individually, like `git add file1.py file2.txt file3.jpeg`
- Optionally, you can check which files and changes you’ve added/staged to the commit using
  - `git status`
- Next, to group these changes together and add a message,
  - `git commit -m “Your custom message!”`
- The `-m` means “use message”, and it will use the next message that you type within quotation marks
- Finally, to sync back with the internet and the online repository,
  - `git push`

