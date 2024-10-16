
#ifndef __SimpleDST_h__
#define __SimpleDST_h__

#include <Rtypes.h>

//======================================================================//
// Establishes SimpleDST class for rapid access to required values      //
// within ROOT tree (located in MasterTree)                             //
//======================================================================//

class TChain;
class TBranch;

class SimpleDST {

 public:

  SimpleDST() { }
  SimpleDST(TChain* chain) { SetupChain(chain); }
  ~SimpleDST() { }

  Int_t Run;
  Double_t ModJulDay;
  UShort_t NStations;
  Bool_t STA3;
  Bool_t STA5;
  Bool_t Reco;

  Double_t PlaneZenith;
  Double_t PlaneAzimuth;
  Bool_t PlaneFitStatus;

  Double_t LaputopZenith;
  Double_t LaputopAzimuth;
  Bool_t LaputopFitStatus;

  TBranch* b_Run;
  TBranch* b_ModJulDay;
  TBranch* b_NStations;
  TBranch* b_STA3;
  TBranch* b_STA5;
  TBranch* b_Reco;

  TBranch* b_PlaneZenith;
  TBranch* b_PlaneAzimuth;
  TBranch* b_PlaneFitStatus;

  TBranch* b_LaputopZenith;
  TBranch* b_LaputopAzimuth;
  TBranch* b_LaputopFitStatus;

  void SetupChain(TChain* chain);

};

#endif // __SimpleDST_h__

