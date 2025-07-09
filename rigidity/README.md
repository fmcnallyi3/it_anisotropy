## Rigidity project (IceCube vs IceTop)

$$
R=\frac{E}{Z}

$$

This folder contains scripts for determining the average composition for use in
anisotropy studies. The end goal should include the following:

* [X] a table of the fractional composition (0.21 p, 0.25 He, etc.) for each energy
  bin in IceCube and each Tier in IceTop
* [X] a table of ln(A) for the same
* [X] a table of average rigidity (E/Z) for the same
* [ ] it probably needs to involve a time-dependent look for IceTop as well...

This folder should eventually be incorporated into the IceTop anisotropy
repository, as created and maintained by Loyola

Files include:

- README.md: this file
- IceTop_partial_comp_dict.ipynb: general notebook for looking at IceTop fractional compositions and rigidity.
- save_data.py: script for saving data to .npy files for running in IceTop_partial_comp_dict