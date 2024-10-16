#include <SimpleDST.h>

#include <TChain.h>
#include <TH1D.h>
#include <TMath.h>
#include <TRandom.h>
#include <TStopwatch.h>

#include <fstream>
#include <iomanip>
#include <sstream>
#include <string>
#include <vector>

// Healpix header files
#include <healpix-cxx/cxxsupport/fitshandle.h>
#include <healpix-cxx/healpix/healpix_map.h>
#include <healpix-cxx/healpix/healpix_map_fitsio.h>
#include <healpix-cxx/cxxsupport/pointing.h>

#include <boost/program_options.hpp>

#include <astro/astro.h>
#include <astro/Astro_Time.h>
#include <astro/Astro_Coords.h>
#include <astro/Astro_Detector.h>

using namespace std;
namespace po = boost::program_options;

const Double_t hour = 1 / 24.;
const Double_t minute = hour / 60.;
const Double_t second = minute / 60.;

void tScramble(po::variables_map vm, vector<string> inFiles);
int tier(string config, SimpleDST dst);


int main(int argc, char* argv[]) {

  po::options_description desc("Allowed options");
  desc.add_options()
      // Options used for all configurations
      ("help", "Produce help message")
      ("batchFile", po::value<string>(), "Text file with input root filenames")
      ("grlFile", po::value<string>(), "Text file with list of good runs")
      ("batch_idx", po::value<string>(), "Line number to read in txt file")
      ("outBase", po::value<string>(), "Base name for outfile")
      ("yyyymmdd", po::value<string>(), "Desired date")
      ("config", po::value<string>(), "Detector configuration")
      ("method", po::value<string>(), "Sidereal, Anti, Solar, Extended")
  ;

  po::variables_map vm;
  // Disable short flags ('-') to allow use of negative signs in input
  po::store(po::parse_command_line(argc, argv, desc,
      po::command_line_style::unix_style ^ po::command_line_style::allow_short),
      vm);

  if (vm.count("help")) {
    cout << desc << "\n";
    return 1;
  }

  // Check for all necessary parameters
  string arr[] = {"outBase", "config", "method", "yyyymmdd"};
  int nKeys = 4;
  vector<string> keyParams(arr, arr+nKeys);
  for (unsigned i = 0; i < keyParams.size(); ++i) {
    if (not vm.count(keyParams[i])) {
      cerr << "\nUsage: " << keyParams[i] << " parameter not defined\n";
      return 1;
    }
  }

  // Read in filelist from batch_idx element of batchfile
  ifstream batchFile(vm["batchFile"].as<string>().c_str());
  string fileListStr;
  int batch_idx = atoi(vm["batch_idx"].as<string>().c_str());
  for (int i = 0; i < batch_idx; ++i)
    getline(batchFile, fileListStr);
  getline(batchFile, fileListStr);
  batchFile.close();

  // Convert fileList string to vector
  istringstream iss(fileListStr);
  vector<string> fileList;
  copy(istream_iterator<string>(iss),
       istream_iterator<string>(),
       back_inserter(fileList));

  cout << "Input files are: " << endl;
  for (unsigned i = 0; i < fileList.size(); ++i)
    cout << fileList[i] << endl;

  tScramble(vm, fileList);

  return 0;
}


void tScramble(po::variables_map vm, vector<string> inFiles_) {

  TStopwatch timer;
  timer.Start();

  // Read input parameters
  string outBase = vm["outBase"].as<string>();
  string config = vm["config"].as<string>();
  string method = vm["method"].as<string>();
  string yyyymmdd = vm["yyyymmdd"].as<string>();

  // Read in good runs from grlFile
  vector<int> runList;
  ifstream grlFile(vm["grlFile"].as<string>().c_str());
  if (grlFile) {
    int run;
    while ( grlFile >> run ) {
      runList.push_back(run);
    }
  }
  grlFile.close();

  // Binning based on NStations -- varies for each detector configuration
  // but there are at most 4 tiers
  unsigned nMaps = 4;

  Astro::IceCubeDetector ice;
  Astro::LocalCoord local;
  Astro::EqCoord eqApparent;

  int NSide = 64;

  // Allow for a map for each energy bin
  cout << "Number of maps: " << nMaps << endl;
  vector< Healpix_Map<float> > LocalMap(nMaps);
  vector< Healpix_Map<float> > DataMap(nMaps);
  vector< Healpix_Map<float> > BGMap(nMaps);

  for (unsigned i = 0; i < nMaps; ++i) {
    LocalMap[i].SetNside(NSide, RING);
    LocalMap[i].fill(0.);
    DataMap[i].SetNside(NSide, RING);
    DataMap[i].fill(0.);
    BGMap[i].SetNside(NSide, RING);
    BGMap[i].fill(0.);
  }

  pointing sphereDir;
  int pixelID;

  stringstream sstr;
  sstr.str("");

  // Establish starting time for desired date
  int yy = atoi(yyyymmdd.substr(0, 4).c_str());
  int mm = atoi(yyyymmdd.substr(5, 2).c_str());
  int dd = atoi(yyyymmdd.substr(7, 2).c_str());
  Astro::Time t(yy, mm, dd, 0, 0, 0);
  double mjd0 = t.GetMJD();

  const char* masterTree = "MasterTree";

  // Initialize the chains and read data
  TChain *cutDST = new TChain(masterTree);
  for (unsigned i = 0; i < inFiles_.size(); ++i)
    cutDST->Add(inFiles_[i].c_str());
  SimpleDST dst(cutDST);

  cout << "Number of chained files: " << cutDST->GetNtrees() << endl;

  Long64_t nEntries = cutDST->GetEntries();
  vector<Long64_t> nEvents(nMaps, 0);
  cout << "Reading " << nEntries << " entries...\n";

  const int nBGResample = 20;
  const double alpha = 1. / nBGResample;
  const double pi = TMath::Pi();

  Double_t mjd1 = mjd0 + 1;
  double zen, azi, theta, phi, rndMJD;
  bool fitStatus;

  // Setup histograms for storing time information
  vector<TH1D*> histMJD(nMaps);
  const char* histName;
  for (unsigned i = 0; i < nMaps; ++i) {
    sstr.str("");
    sstr << "histMJD_" << i;
    histName = sstr.str().c_str();
    histMJD[i] = new TH1D(histName, ";modified julian day;events",
    Int_t((mjd1 - mjd0) / (10. * second)), mjd0, mjd1);
  }

  // Track the local coordinates
  vector< vector<Double_t> > LocCoord_theta(nMaps);
  vector< vector<Double_t> > LocCoord_phi(nMaps);

  // Pole cut values for directional reconstructions
  const Double_t zLo = 0.002;                  // 0.11 degrees
  const Double_t zHi = TMath::Pi() - 0.002;    // 179.89 degrees

  //*********************************************************************//
  // Begin iterating through events
  //*********************************************************************//
  int mapIdx;
  int lastRun = 0;

  // Iterate over all events, storing local and equatorial coordinates and
  // arrival times.
  // Note: cannot stop early because events can be out of time order
  //for (Long64_t jentry=0; jentry<nEntries; ++jentry) {
  // NOTE: WRITTEN TO ONLY RUN OVER FIRST 20 ENTRIES AS A TEST
  for (Long64_t jentry=0; jentry<20; ++jentry) {

    cutDST->GetEntry(jentry);

    //*********************************************************************//
    // Event cuts
    //*********************************************************************//

    // NOTE: TIME CUTS IGNORED WHILE TESTING LAPUTOP RECO BEHAVIOR
    // Basic time check
    //if (dst.ModJulDay < mjd0) {
    //  if (jentry % 10000000 == 0)
    //    cout << "Processed " << jentry << " entries before starting..." << endl;
    //  continue;
    //}
    //if (dst.ModJulDay > mjd1)
    //  continue;

    // Print update on run number
    if (dst.Run != lastRun) {
      cout << "Starting run #" << dst.Run << "..." << endl;
      lastRun = dst.Run;
    }

    // Must pass STA3 or STA5 filter
    if (!dst.STA3 && !dst.STA5)
      continue;

    // Identify energy tier based on nstations value
    mapIdx = tier(config, dst);

    // Remove events with nstations below the minimum threshold
    if (mapIdx == -1)
      continue;

    // Values for zenith and azimuth already stored in radians
    if (mapIdx == 0) {
      zen = dst.PlaneZenith;
      azi = dst.PlaneAzimuth;
      // Can't figure out how to do fit status on ShowerPlane (always passes?)
      // fitStatus = dst.PlaneFitStatus;
      fitStatus = true;
    }
    else {
      zen = dst.LaputopZenith;
      azi = dst.LaputopAzimuth;
      fitStatus = dst.Reco;
      //cout << "fitStatus: " << fitStatus << endl;
    }
    cout << "Entry #: " << jentry << endl;
    cout << "dst.Reco: " << dst.Reco << endl;

    // SimpleDST cuts (automatically included in Segev-processed files)
    // First: throw away reconstructions too close to poles
    if (zen < zLo || zen > zHi)
      continue;

    // Reconstruction cuts
    if (!fitStatus || zen != zen || azi != azi)
      continue;

    // Ensure run is in good run list
    if (std::find(runList.begin(), runList.end(), dst.Run) == runList.end())
      continue;

    //*********************************************************************//
    // Store information for events that pass cuts
    //*********************************************************************//

    // Store local coordinates
    ++nEvents[mapIdx];
    LocCoord_theta[mapIdx].push_back(zen);
    LocCoord_phi[mapIdx].push_back(azi);
    sphereDir.theta = zen;
    sphereDir.phi = azi;
    pixelID = LocalMap[mapIdx].ang2pix(sphereDir);

    // All events evenly weighted (adjustable for future solar dipole sub.)
    t.SetTime(dst.ModJulDay);
    local.SetLocalRad(zen, azi);
    eqApparent = ice.LocalToEquatorial(local, t);
    double eventweight = 1.0;
    LocalMap[mapIdx][pixelID] += eventweight;

    // Calculate equatorial coordinates in other time frame
    if (method == "anti")
      eqApparent = ice.LocalToEquatorial_FromAntiSid(local, t);
    if (method == "ext")
      eqApparent = ice.LocalToEquatorial_FromExtendedSid(local, t);
    if (method == "solar")
      eqApparent = ice.LocalToEquatorial_FromSolar(local, t);

    // Write to map
    sphereDir.theta = pi/2. - eqApparent.GetDecRad();
    sphereDir.phi = eqApparent.GetRaRad();
    // Solar coordinates need a 180 deg flip in phi (definition difference)
    if (method == "solar")
      sphereDir.phi -= pi;
    while (sphereDir.phi < 0)
      sphereDir.phi += 2.*pi;
    pixelID = DataMap[mapIdx].ang2pix(sphereDir);
    DataMap[mapIdx][pixelID] += eventweight;

    // Store time
    histMJD[mapIdx]->Fill(dst.ModJulDay);
  }

  //*********************************************************************//
  // Scramble the maps
  //*********************************************************************/  /

  for (unsigned mEntry = 0; mEntry<nMaps; mEntry++) {

    cout << "Working on Tier " << mEntry << "..." << endl;

    // Scramble the time
    cout << "  Scrambling time for (" << nBGResample << "x "
         << nEvents[mEntry] << " events)..." << endl;
    gRandom->SetSeed(0);

    for (Long64_t iEntry=0; iEntry<(Long64_t)(nEvents[mEntry]); iEntry++) {

      // Get local coordinates
      theta = LocCoord_theta[mEntry][iEntry];
      phi = LocCoord_phi[mEntry][iEntry];
      local.SetLocalRad(theta, phi);

      // Create nBGResample fake events for each real event
      for (int k=0; k<nBGResample; ++k) {

        // Generate new equatorial coordinates
        rndMJD = histMJD[mEntry]->GetRandom();
        t.SetTime(rndMJD);
        if (method == "anti")
          eqApparent = ice.LocalToEquatorial_FromAntiSid(local, t);
        if (method == "ext")
          eqApparent = ice.LocalToEquatorial_FromExtendedSid(local, t);
        if (method == "sid")
          eqApparent = ice.LocalToEquatorial(local, t);
        if (method == "solar")
          eqApparent = ice.LocalToEquatorial_FromSolar(local, t);

        // Write to map
        sphereDir.theta = (pi/2. - eqApparent.GetDecRad());
        sphereDir.phi = eqApparent.GetRaRad();
        if (method == "solar")
          sphereDir.phi -= pi;
        while (sphereDir.phi < 0)
          sphereDir.phi += 2.*pi;
        pixelID = DataMap[mEntry].ang2pix(sphereDir);

        BGMap[mEntry][pixelID] += 1.0;
      }
    }
  }

  for (unsigned m=0; m<nMaps; ++m) {

    // Skip lower tiers for later years
    if (config=="IT81-2015" || config=="IT81-2016" ||
        config=="IT81-2017" || config=="IT81-2018" ||
        config=="IT81-2019" || config=="IT81-2020" ||
        config=="IT81-2021") {
      if (m==0 || m==1)
        continue;
    }

    // Scale background map
    for (int i=0; i<BGMap[m].Npix(); ++i)
      BGMap[m][i] *= alpha;

    cout << "Read " << nEntries << " events" << "\n"
         << "Used " << nEvents[m] << " events" << endl;

    // Save BG, Data, and Local maps in one file
    arr<std::string> colname(3);
    colname[0] = "data map";
    colname[1] = "background map";
    colname[2] = "local map";

    // Automatically create output file name
    sstr.str("");
    sstr << outBase << "_" << yyyymmdd << "_Tier" << m+1 << ".fits";
    fitshandle fitsOut;
    fitsOut.create(sstr.str().c_str());

    // Save to file
    fitsOut.add_comment("Maps: data, bg, local");
    prepare_Healpix_fitsmap(fitsOut, DataMap[m], 
        FITSUTIL<float>::DTYPE, colname);
    fitsOut.write_column(1, DataMap[m].Map());
    fitsOut.write_column(2, BGMap[m].Map());
    fitsOut.write_column(3, LocalMap[m].Map());
    fitsOut.close();
  }

  // Clean up
  delete cutDST;
  for (unsigned m=0; m<nMaps; ++m)
    delete histMJD[m];

  timer.Stop();
  printf("RT=%7.3f s, Cpu=%7.3f s\n",timer.RealTime(),timer.CpuTime());

}


int tier(string config, SimpleDST dst) {

  // Different tier values depending on detector configuration and NStations
  int nstations = dst.NStations;

  if (config=="IT81-2011") {
    if (nstations>=3 && nstations<5)
      return 0;
    else if (nstations>=5 && nstations<10)
      return 1;
    else if (nstations>=10 && nstations<17)
      return 2;
    else if (nstations>=17)
      return 3;
  }

  else if (config=="IT81-2012" || config=="IT81-2013") {
    if (nstations>=3 && nstations<5)
      return 0;
    else if (nstations>=5 && nstations<9)
      return 1;
    else if (nstations>=9 && nstations<16)
      return 2;
    else if (nstations>=16)
      return 3;
  }

  else if (config=="IT81-2014") {
    if (nstations>=3 && nstations<5)
      return 0;
    else if (nstations>=5 && nstations<8)
      return 1;
    else if (nstations>=8 && nstations<15)
      return 2;
    else if (nstations>=15)
      return 3;
  }

  else if (config=="IT81-2015") {
    if (nstations>=8 && nstations<15)
      return 2;
    else if (nstations>=15)
      return 3;
  }

  else if (config=="IT81-2016" || config=="IT81-2017") {
    if (nstations>=7 && nstations<14)
      return 2;
    else if (nstations>=14)
      return 3;
  }

  else if (config=="IT81-2018" || config=="IT81-2019") {
    if (nstations>=6 && nstations<13)
      return 2;
    else if (nstations>=13)
      return 3;
  }

  else if (config=="IT81-2020" || config=="IT81-2021") {
    if (nstations>=5 && nstations<12)
      return 2;
    else if (nstations>=12)
      return 3;
  }

  return -1;
}







