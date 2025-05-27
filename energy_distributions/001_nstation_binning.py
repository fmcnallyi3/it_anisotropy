# imports
import argparse
import ast
import numpy as np
import matplotlib.pyplot as plt
import math
import h5py, glob
import pandas as pd
import tables
import simweights
from icecube.weighting import weighting
from icecube.weighting.fluxes import GaisserH4a_IT

# There are 4 simulations in the folder
# dataset 12360 PPlus       = 2212
# dataset 12630 He4Nucleus  = 1000020040
# dataset 12631 O16Nucleus  = 1000080160
# dataset 12362 Fe56Nucleus = 1000260560
#fnum = [12360, 12630, 12631, 12362]  # file number
fnum = [22570, 22580, 22583, 22586]  # file number
ptype = [2212, 1000020040, 1000080160, 1000260560]  # particle type
# In order: proton, helium, oxygen, iron

# Define flux model used for icecube weighting
flux = simweights.GaisserH4a_IT()

"""
Naming convention:

Prefixes
mc-  = Monte Carlo (Simulation)
lap- = Laputop (Reconstructed Simulation)
sp-  = ShowerPlane (Reconstructed Simulation)
p-   = Proton
he-  = Helium
o-   = Oxygen
fe-  = Iron

-en  = Energy
-zen = Zenith
-az  = Azimuth
-w   = Weighting
-stations = number of stations each events triggers

"""


def get_array(indir, j, it73c=0):
    """Reads hdf5 file that contains simulation information for one particle,
    applies specified permutation of IT73 quality cuts, and returns a list
    with the true and reconstructed energy, angle and number of stations.

    Inputs
    -----
    indir : String
        Path to input directory containing hdf5 files

    j : Integer from 0 to 3.
        Index of particle type.
        0 -> proton
        1 -> helium
        2 -> oxygen
        3 -> iron

    it73c: Integer from 0 to 2
        Index of IT73 Quality Cuts Permutation
        0 -> No quality cuts [what we used in our analysis]
        1 -> IceTop_reco_succeeded is applied
        2 -> All IT73 Quality Cuts are applied

    Returns
    -----
    output : list
        [mcen, mczen, mcaz, mcw, lapzen, lapaz, lapw, spzen, spaz, spw, stations]
        See naming conventions above for further clarification
    """
    # Read file
    f = h5py.File(indir + '/l3_{}.hdf5'.format(fnum[j]), 'r')

    # Save stations
    s = np.array(f['NStations']['value'])

    # Save each IT73 quality cut individually
    cut5 = np.array(f['IT73AnalysisIceTopQualityCuts']['BetaCutPassed'])
    cut6 = np.array(f['IT73AnalysisIceTopQualityCuts']['IceTopMaxSignalAbove6'])
    cut7 = np.array(f['IT73AnalysisIceTopQualityCuts']['IceTopMaxSignalInside'])
    cut8 = np.array(f['IT73AnalysisIceTopQualityCuts']['IceTopNeighbourMaxSignalAbove4'])
    cut9 = np.array(f['IT73AnalysisIceTopQualityCuts']['IceTop_StandardFilter'])
    cut10 = np.array(f['IT73AnalysisIceTopQualityCuts']['IceTop_reco_succeeded'])
    cut11 = np.array(f['IT73AnalysisIceTopQualityCuts']['Laputop_FractionContainment'])
    cut12 = np.array(f['IT73AnalysisIceTopQualityCuts']['StationDensity_passed'])

    # Append all data onto 'master' arrays
    en = np.array(f['MCPrimary']['energy'])
    zen = np.array(np.rad2deg(f['MCPrimary']['zenith']))
    az = np.array(np.rad2deg(f['MCPrimary']['azimuth']))

    lapzen = np.array(np.rad2deg(f['Laputop']['zenith']))
    lapaz = np.array(np.rad2deg(f['Laputop']['azimuth']))
    spzen = np.array(np.rad2deg(f['ShowerPlane']['zenith']))
    spaz = np.array(np.rad2deg(f['ShowerPlane']['azimuth']))

    # Get weighting from icecube (1 using mcprimary zenith and 1 for each
    # reconstructed zenith)

    file_obj = tables.open_file(indir+'/l3_{}.hdf5'.format(fnum[j]), "r")
    weighter = simweights.IceTopWeighter(file_obj)
    weights = weighter.get_weights(flux)

    mcw = weights
    lapw = weights
    spw = weights

    """
    generator = weighting.from_simprod(fnum[j])
    generator *= 20000
    a = flux(f['MCPrimary']['energy'], ptype[j])
    b = generator(f['MCPrimary']['energy'], ptype[j], np.cos(f['MCPrimary']['zenith']))
    mcw = a / b

    c = generator(f['MCPrimary']['energy'], ptype[j], np.cos(f['Laputop']['zenith']))
    lapw = a / c

    d = generator(f['MCPrimary']['energy'], ptype[j], np.cos(f['ShowerPlane']['zenith']))
    spw = (a / d)
    """



    # Store array of number of stations activated by proton events
    stations = np.array(f['NStations']['value'])
    stations = np.array(stations)

    # Check if inf or NaN are being included
    mcw[np.isinf(mcw)] = 0
    lapw[np.isinf(lapw)] = 0
    spw[np.isinf(spw)] = 0
    
    mcw[np.isnan(mcw)] = 0
    lapw[np.isnan(lapw)] = 0
    spw[np.isnan(spw)] = 0

    # Apply specified IT73 Quality Cuts
    if (it73c == 1):
        cut = cut10
        it73_a = np.where(cut == 1, cut, 0)
    elif (it73c == 2):
        cut = cut5 + cut6 + cut7 + cut8 + cut9 + cut10 + cut11 + cut12
        it73_a = np.where(cut == 8, cut, 0)
    else:
        it73_a = np.ones_like(s)

    output = [en, zen, az, mcw, lapzen, lapaz, lapw,
              spzen, spaz, spw, stations]
    for ind, arr in enumerate(output):
        output[ind] = arr[np.where(it73_a != 0)]

    return output


def get_all_particles(indir, it73=0):
    """
    Gets list of parameters for all particles given input directory and index
    of permutation for IT73 Quality Cuts.

    Inputs
    -----
    Indir : String
        Path to input directory containing the hdf5 files

    it73: Integer from 0 to 2, optional
        Index of IT73 Quality Cuts Permutation
        0 -> No quality cuts [what we used in our analysis]
        1 -> IceTop_reco_succeeded is applied
        2 -> All IT73 Quality Cuts are applied

    Returns
    ------
    particles : list
        2D list. Each element is the list of parameters for a particle type
        [[Proton], [Helium], [Oxygen], [Iron]]
    """

    particles = []
    for j in range(len(fnum)):
        particle = get_array(indir, j, it73)
        particles.append(particle)
    return particles


def get_prot_iron(indir, it73=0):
    """
    Gets list of parameters for proton and iron given input directory and index
    of permutation for IT73 Quality Cuts.

    Inputs
    -----
    Indir : String
        Path to input directory containing the hdf5 files

    it73: Integer from 0 to 2, optional
        Index of IT73 Quality Cuts Permutation
        0 -> No quality cuts [what we used in our analysis]
        1 -> IceTop_reco_succeeded is applied
        2 -> All IT73 Quality Cuts are applied

    Returns
    ------
    particles : list
        2D list. Each element is the list of parameters for a particle type
        [[Proton], [Iron]]
    """

    arr = get_all_particles(indir, it73)
    # Proton, Iron
    return [arr[0], arr[3]]

def get_prot(indir, it73=0):
    """
    Gets list of parameters for proton and iron given input directory and index
    of permutation for IT73 Quality Cuts.

    Inputs
    -----
    Indir : String
        Path to input directory containing the hdf5 files

    it73: Integer from 0 to 2, optional
        Index of IT73 Quality Cuts Permutation
        0 -> No quality cuts [what we used in our analysis]
        1 -> IceTop_reco_succeeded is applied
        2 -> All IT73 Quality Cuts are applied

    Returns
    ------
    particles : list
        2D list. Each element is the list of parameters for a particle type
        [[Proton], [Iron]]
    """

    arr = get_all_particles(indir, it73)
    # Proton, Iron
    return [arr[0]]


def save_all_as_npy(indir, outdir, energies, it73=0):
    """
    # Given an input directory containing hdf5 simulation files, for each of
    all four particles: apply specified IT73 Quality Cuts, bin by stations
    triggered, and save each parameter list as numpy arrays for quicker future
    processing.

    :param indir: String
        Path to input directory containing the hdf5 files

    :param outdir: String
        Path to output directory where the .npy arrays will be saved

    :param energies: list
        Each element is a list of length two, containing the low
        and high bounds of each energy bin. E.g. energies = [[3,5]] means a
        low energy bin for 3 <= number of stations < 5, and a high energy bin
        for 5 <= number of stations

    :param it73: Integer from 0 to 2, optional
        Index of IT73 Quality Cuts Permutation
        0 -> No quality cuts [what we used in our analysis]
        1 -> IceTop_reco_succeeded is applied
        2 -> All IT73 Quality Cuts are applied

    :return: None
    """

    dat = get_all_particles(indir, it73)
    particles = [[[0 for i in range(11)] for j in range(4)] for k in range(4)]

    for i, particle in enumerate(dat):
        # Cut events where mczen/mcaz/lapzen/lapaz is nan [also eliminates for sp]
        mczen = particle[1]
        mcaz = particle[2]
        index_0 = np.argwhere(np.isnan(mczen))
        index_1 = np.argwhere(np.isnan(mcaz))

        lapzen = particle[4]
        lapaz = particle[5]
        index_2 = np.argwhere(np.isnan(lapzen))
        index_3 = np.argwhere(np.isnan(lapaz))

        for ind, arr in enumerate(particle):
            particle[ind] = np.delete(arr, index_0)
            particle[ind] = np.delete(arr, index_1)
            particle[ind] = np.delete(arr, index_2)
            particle[ind] = np.delete(arr, index_3)

        # Bin by number of stations triggered
        stations = particle[10]
        for index, [low, high] in enumerate(energies):
            for ind, arr in enumerate(particle):
                if ind != 10:
                    particles[i][index][ind] = arr[np.where((stations >= low)
                                                            & (stations < high))]
                else:
                    particles[i][index][ind] = arr

        # Highest energy bin has no upper bound
        for ind, arr in enumerate(particle):
            if ind != 10:
                particles[i][-1][ind] = arr[np.where((stations >= high))]
            else:
                particles[i][i - 1][ind] = arr

    # Save arrays

    # For naming reference
    Particles = ["Proton", "Helium", "Oxygen", "Iron"]
    Energies = ["T1", "T2", "T3", "T4"]
    Origin = ["MC", "Laputop", "ShowerPlane"]
    Parameters = ["Zenith", "Azimuth", "Weights"]

    for i, particle in enumerate(particles):
        for index, tier in enumerate(particle):
            for ind, arr in enumerate(tier):
                # Save True Energy and Stations separately
                if (ind == 0):
                    np.save(outdir + '/' + Particles[i] + "-" + Energies[index]
                            + "-MC-Energy", arr)
                elif (ind == 10):
                    np.save(outdir + '/' + Particles[i] + "-" + Energies[index]
                            + "-Stations", arr)
                else:
                    param_ind = (ind - 1) % 3
                    orig_ind = math.floor((ind - 1) / 3)
                    np.save(
                        outdir + '/' + Particles[i] + "-" + Energies[index]
                        + "-" + Origin[orig_ind] + "-" + Parameters[param_ind],
                        arr)


if __name__ == "__main__":
    # Set up command line options
    parser = argparse.ArgumentParser(description=
                                     "Process simulation hdf5 files as .npy arrays")
    parser.add_argument('simulation_directory', type=str,
                        help="Directory where sim hdf5 files are stored")
    parser.add_argument("--it73", dest="it73", type=int, default=0,
                        help="Choose what IT73 cuts to apply")
    parser.add_argument("-o", "--output", dest="output", type=str,
                        default='./arrays', help="Output directory of .npy arrays")
    parser.add_argument("-e", "--energies", dest='energies', type=str,
                        default='[[3, 5], [5, 9], [9, 16]]',
                        help="NStation boundaries for each energy tier/band")
    args = parser.parse_args()
        
    # Parse energies as list of lists
    if args.energies is not None:
        try:
            bins = ast.literal_eval(args.energies)
            if not all(isinstance(inner_list, list) and all(isinstance(i, int) for i in inner_list) for inner_list in bins):
                raise ValueError
        except (ValueError, SyntaxError):
            print(f"Error: The provided list of lists '{args.energies}' is not valid.")
            sys.exit(1)

    save_all_as_npy(args.simulation_directory, args.output, bins, args.it73)
