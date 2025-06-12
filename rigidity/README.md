## Rigidity project (IceCube vs IceTop)
This folder contains scripts for determining the average composition for use in
anisotropy studies. The end goal should include the following:
- a table of the fractional composition (0.21 p, 0.25 He, etc.) for each energy
  bin in IceCube and each Tier in IceTop
- a table of ln(A) for the same
- a table of average rigidity (E/Z) for the same
- it probably needs to involve a time-dependent look for IceTop as well...

To accomplish this, we should create a notebook that does all of this; it takes
the number of events for each composition in an energy bin, divides that by the
total number of events in that bin, and outputs the result to a table; it takes
the natural log of the atomic number of the particle event in an energy bin, and
outputs the result to the table; it takes the energy and divides it by the
charge of the particle of an event in an energy bin, and oputs the result to the
table.

Files include:
- README.md: this file
- it_comp.py: starter script for looking at IceTop composition
- it_comp.ipynb: an attempt to do these steps with a jupyter notebook. Fails
  because the kernel doesn't have access to simweights and I haven't spent the
time figuring out how to set it up