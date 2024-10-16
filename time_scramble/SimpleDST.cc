#include <SimpleDST.h>
#include <string>
#include <TBranch.h>
#include <TChain.h>

//======================================================================//
// Creates pointers to fill the SimpleDST class (info in MasterTree)    //
//======================================================================//

void
SimpleDST::SetupChain(TChain* chain)
{

  chain->SetBranchAddress("I3EventHeader.Run", &Run, &b_Run);
  chain->SetBranchAddress("I3EventHeader.time_start_mjd", &ModJulDay, &b_ModJulDay);
  chain->SetBranchAddress("NStations.value", &NStations, &b_NStations);
  chain->SetBranchAddress("QFilterMask.IceTopSTA3_13", &STA3, &b_STA3);
  chain->SetBranchAddress("QFilterMask.IceTopSTA5_13", &STA5, &b_STA5);
  chain->SetBranchAddress("IT73AnalysisIceTopQualityCuts.IceTop_reco_succeeded", &Reco, &b_Reco);

  // ShowerPlane information
  chain->SetBranchAddress("ShowerPlane.zenith", &PlaneZenith, &b_PlaneZenith);
  chain->SetBranchAddress("ShowerPlane.azimuth", &PlaneAzimuth, &b_PlaneAzimuth);
  chain->SetBranchAddress("ShowerPlane.fit_status", &PlaneFitStatus, &b_PlaneFitStatus);

  // Laputop information
  chain->SetBranchAddress("Laputop.zenith", &LaputopZenith, &b_LaputopZenith);
  chain->SetBranchAddress("Laputop.azimuth", &LaputopAzimuth, &b_LaputopAzimuth);
  chain->SetBranchAddress("Laputop.fit_status", &LaputopFitStatus, &b_LaputopFitStatus);

}

