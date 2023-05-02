#!/usr/bin/env python
# coding: utf-8

# In[1]:


import ROOT
from ROOT import VecOps
import numpy as np
import sys


# In[2]:


def deltar(eta1, eta2, phi1, phi2):
    x = ROOT.VecOps.DeltaR(eta1, eta2, phi1, phi2)
    return(x)


# In[3]:


def getGenIndex(t):
    genIdx={}
    gen_id = t.GenPart_pdgId
    mthr_idx = t.GenPart_genPartIdxMother
    for i in range(t.nGenPart):
        if gen_id[i]==9000022:
            genIdx["akk"]=i
        if gen_id[i]==9000025:
            genIdx["radion"]=i
        if mthr_idx[i]>=0:
            if gen_id[i]==22 and (gen_id[mthr_idx[i]]==9000022 or mthr_idx[i]==0) :
                genIdx["photon"]=i
            if gen_id[i]==24:
                genIdx["wp"]=i
            if gen_id[i]==-24:
                genIdx["wm"]=i
            if abs(gen_id[i])<20:
                if gen_id[mthr_idx[i]]==24:
                    if "wp0" in genIdx:
                        genIdx["wp1"]=i
                    else:
                        genIdx["wp0"]=i
                if gen_id[mthr_idx[i]]==-24:
                    if "wm0" in genIdx:
                        genIdx["wm1"]=i
                    else:
                        genIdx["wm0"]=i

    # print("genIdx",genIdx)
    return genIdx
    


# In[4]:


def myphoton(t):
    """
    find iso_photons
    input:  t= tree for this event
    output: iso_photons_idx= list of index
    """
    photon_id=t.Photon_mvaID_WP90
    photon_seed=t.Photon_pixelSeed
    photon_pt=t.Photon_pt
    iso_photons_idx = []
    nphotons = len(photon_id)
    #print(nphotons)
    if nphotons > 0:
        for i in range(nphotons):
            if (photon_id[i] == 1) and (photon_seed[i] == 0):
                iso_photons_idx.append(i)
            else:
                continue
    return iso_photons_idx 


# In[5]:


def cleanedjets(t):
    jet_eta=t.FatJet_eta
    jet_phi=t.FatJet_phi
    jet_mass=t.FatJet_msoftdrop
    jet_jetId=t.FatJet_jetId
    
    photon_eta=t.Photon_eta
    photon_phi=t.Photon_phi
    photon_id=t.Photon_mvaID_WP90
    photon_seed=t.Photon_pixelSeed
    photon_pt=t.Photon_pt
      
    jets_idx = []
    nfatjets = len(jet_eta)
    # photons = myphoton(photon_id, photon_seed, photon_pt)
    photons = myphoton(t)
    if nfatjets >= 0:
        for k in range(nfatjets):
            iskip=0
            for ip, p in enumerate(photons):
                if (abs(ROOT.VecOps.DeltaR(jet_eta[k], photon_eta[p], jet_phi[k], photon_phi[p]))) < 0.4:
                    iskip=1
                    break

            if iskip==0:
                jets_idx.append(k)
    
    return jets_idx


# In[6]:


def print_event(it, t, alist):
    """
    alsit: list of objects to print. Available keys are,
    met
    genPart, genPart_all
    recoPhoton, recoPhoton_all
    recoFatjet, recoFatjet_all
    recoElectron_all
    recoMuon_all
    []    for all objects
    ["met","genPart","recoPhoton","recoPhoton_all","recoFatjet","recoFatjet_all","recoElectron_all","recoMuon_all"]
    """

    
    print()
    print("Event: ",it)
    
    """
    MET
    """
    def printMET():
        print("=== MET ")
        print("   GenMET pt {:8.1f}".format(t.GenMET_pt),end="")
        print("     phi {:8.1f}".format(t.GenMET_phi),end="")
        print(" ")
        print("   MET    pt {:8.1f}".format(t.MET_pt),end="")
        print("     phi {:8.1f}".format(t.MET_phi),end="")
        print(" ")
        
    if ("met" in alist) or len(alist)==0:
        printMET()
        
    """
    GenParticle
    """
    def print_aGenPart_Header(title):
        print("=== GenPart ",title)
        print("{:>4s}".format("  "),end="")
        print("{:>4s}".format("stat"),end="")
        print("{:>8s}".format("id"),end="")
        print("{:>6s}".format("moth"),end="")
        print("{:>8s}".format("pt"),end="")
        print("{:>8s}".format("eta"),end="")
        print("{:>8s}".format("phi"),end="")
        print("{:>8s}".format("mass"),end="")
        print()
        
    def print_aGenPart(ix):
        print("{:4d}".format(ix),end="")
        print("{:4d}".format(t.GenPart_status[ix]),end="")
        print("{:8d}".format(t.GenPart_pdgId[ix]),end="")
        print("{:6d}".format(t.GenPart_genPartIdxMother[ix]),end="")
        print("{:8.1f}".format(t.GenPart_pt[ix]),end="")
        print("{:8.2f}".format(t.GenPart_eta[ix]),end="")
        print("{:8.2f}".format(t.GenPart_phi[ix]),end="")
        print("{:8.1f}".format(t.GenPart_mass[ix]),end="")
        print()
    
    if ("genPart" in alist) or len(alist)==0:
        print_aGenPart_Header("")  #  print a header
    
        genIdx=getGenIndex(t)  #   get a dictionary of genpart index
        for key in genIdx:
            # print("key",key)
            ix=genIdx[key]
            print_aGenPart(ix)
            
    if ("genPart_all" in alist) or len(alist)==0:
        print_aGenPart_Header("(all)")  #  print a header
        for ix in range(t.nGenPart):
            print_aGenPart(ix)

    """
    RecoPhoton
    """
    def print_recoPhoton_Header(title):
        print("=== Reco Photon ",title)
        print("{:>4s}".format("  "),end="")
        print("{:>8s}".format("id"),end="")
        print("{:>8s}".format("pt"),end="")
        print("{:>8s}".format("eta"),end="")
        print("{:>8s}".format("phi"),end="")
        print()
    
    def print_recoPhoton(ix):
        print("{:4d}".format(ix),end="")
        print("{:8d}".format(t.Photon_mvaID_WP90[ix]),end="")
        print("{:8.1f}".format(t.Photon_pt[ix]),end="")
        print("{:8.2f}".format(t.Photon_eta[ix]),end="")
        print("{:8.2f}".format(t.Photon_phi[ix]),end="")
        print()
        
    if ("recoPhoton" in alist) or len(alist)==0:
        iso_photon_idx=myphoton(t)
        if len(iso_photon_idx)>0:
            print_recoPhoton_Header("")
            for ix in iso_photon_idx:
                print_recoPhoton(ix)
        
    if ("recoPhoton_all" in alist) or len(alist)==0:
        if t.nPhoton>0:
            print_recoPhoton_Header("(all)")
            for ix in np.arange(t.nPhoton):
                print_recoPhoton(ix)

    """
    RecoFatJet
    """
    def print_recoFatjet_Header(title):
        print("=== Reco Fatjet ",title)
        print("{:>4s}".format("  "),end="")
        print("{:>8s}".format("id"),end="")
        print("{:>8s}".format("pt"),end="")
        print("{:>8s}".format("eta"),end="")
        print("{:>8s}".format("phi"),end="")
        print("{:>8s}".format("sd mass"),end="")
        print()
    
    def print_recoFatjet(ix):
        print("{:4d}".format(ix),end="")
        print("{:8d}".format(t.FatJet_jetId[ix]),end="")
        print("{:8.1f}".format(t.FatJet_pt[ix]),end="")
        print("{:8.2f}".format(t.FatJet_eta[ix]),end="")
        print("{:8.2f}".format(t.FatJet_phi[ix]),end="")
        print("{:8.1f}".format(t.FatJet_msoftdrop[ix]),end="")
        print() 

    if ("recoFatjet" in alist) or len(alist)==0:
        jets_idx=cleanedjets(t)
        if len(jets_idx)>0:
            print_recoFatjet_Header("")
            for ix in jets_idx:
                print_recoFatjet(ix)
            
    if ("recoFatjet_all" in alist) or len(alist)==0:
        if t.nFatJet>0:
            print_recoFatjet_Header("(all)")
            for ix in np.arange(t.nFatJet):
                print_recoFatjet(ix)

    """
    RecoElectron
    """        

    def print_recoElectron_Header(title):
        print("=== Reco Electron ",title)
        print("{:>4s}".format("  "),end="")
        print("{:>8s}".format("pt"),end="")
        print("{:>8s}".format("eta"),end="")
        print("{:>8s}".format("phi"),end="")
        print()
    
    def print_recoElectron(ix):
        print("{:4d}".format(ix),end="")
        print("{:8.1f}".format(t.Electron_pt[ix]),end="")
        print("{:8.2f}".format(t.Electron_eta[ix]),end="")
        print("{:8.2f}".format(t.Electron_phi[ix]),end="")
        print() 
        
    if ("recoElectron_all" in alist) or len(alist)==0:
        if t.nElectron>0:
            print_recoElectron_Header("(all)")
            for ix in np.arange(t.nElectron):
                print_recoElectron(ix)

    """
    RecoMuon
    """
    def print_recoMuon_Header(title):
        print("=== Reco Muon ",title)
        print("{:>4s}".format("  "),end="")
        print("{:>8s}".format("pt"),end="")
        print("{:>8s}".format("eta"),end="")
        print("{:>8s}".format("phi"),end="")
        print()
    
    def print_recoMuon(ix):
        print("{:4d}".format(ix),end="")
        print("{:8.1f}".format(t.Muon_pt[ix]),end="")
        print("{:8.2f}".format(t.Muon_eta[ix]),end="")
        print("{:8.2f}".format(t.Muon_phi[ix]),end="")
        print() 

    if ("recoMuon_all" in alist) or len(alist)==0:
        if t.nMuon>0:
            print_recoMuon_Header("(all)")
            for ix in np.arange(t.nMuon):
                print_recoMuon(ix)
            
    """
    RecoTau
    """
    def print_recoTau_Header(title):
        print("=== Reco Tau === ",title)
        print("{:>4s}".format("  "),end="")
        print("{:>8s}".format("pt"),end="")
        print("{:>8s}".format("eta"),end="")
        print("{:>8s}".format("phi"),end="")
        print()
    
    def print_recoTau(ix):
        print("{:4d}".format(ix),end="")
        print("{:8.1f}".format(t.Tau_pt[ix]),end="")
        print("{:8.2f}".format(t.Tau_eta[ix]),end="")
        print("{:8.2f}".format(t.Tau_phi[ix]),end="")
        print() 

    if ("recoTau_all" in alist) or len(alist)==0:
        if t.nTau>0:
            print_recoTau_Header("(all)")
            for ix in np.arange(t.nTau):
                print_recoTau(ix)


# In[7]:


class test_myphoton():
    def __init__(self):
        self.h1={}
        s="photon_n"
        self.h1[s] = ROOT.TH1F(s,s,10,0.,10.)
        s="photon_pt"
        self.h1[s] = ROOT.TH1F(s,s,100,0.,2000.)
        s="photon_eta"
        self.h1[s] = ROOT.TH1F(s,s,100,-5.0,5.0)
        s="photon_phi"
        self.h1[s] = ROOT.TH1F(s,s,100,0.0,4.0)
    
    def analyze(self,t):
                
        iso_photon_idx=myphoton(t)
        n=len(iso_photon_idx)
        print("iso_photon n=",n," idx",iso_photon_idx)
        
        self.h1["photon_n"].Fill(n)
        
        for i,idx in enumerate(iso_photon_idx):
            # print("i",i,"idx",idx)
            pt=t.Photon_pt[idx]
            eta=t.Photon_eta[idx]
            phi=t.Photon_phi[idx]
            self.h1["photon_pt"].Fill(pt)
            self.h1["photon_eta"].Fill(eta)
            self.h1["photon_phi"].Fill(phi)
    
    def endjob(self):
        print("test_myphoton::endjob")
        c1 = ROOT.TCanvas("c1","test_myphoton",800,600)
        print("in endjob0")
        c1.Divide(2,2)
        c1.cd(1)
        s="photon_n"
        self.h1[s].Draw()
        c1.cd(2)
        s="photon_pt"
        self.h1[s].Draw()
        c1.cd(3)
        s="photon_eta"
        self.h1[s].Draw()
        c1.cd(4)
        s="photon_phi"
        self.h1[s].Draw()
        print("in endjob5")
        
        #  c1.Draw()  # Draw does not work here...
        c1.SaveAs("test_myphoton.pdf")
        #  for testing on mac
        # !open "test_myphoton.pdf"
        return


# In[8]:


class test_cleanedjets():
    def __init__(self):
        self.h1={}
        s="fatjet_n"
        self.h1[s] = ROOT.TH1F(s,s,10,0.,10.)
        s="fatjet_pt"
        self.h1[s] = ROOT.TH1F(s,s,100,0.,2000.)
        s="fatjet_eta"
        self.h1[s] = ROOT.TH1F(s,s,100,-5.0,5.0)
        s="fatjet_phi"
        self.h1[s] = ROOT.TH1F(s,s,100,0.0,4.0)
    
    def analyze(self,t):
        fatjet_idx=cleanedjets(t)
        n=len(fatjet_idx)
        print("fatjet n=",n," idx",fatjet_idx)
        
        self.h1["fatjet_n"].Fill(n)
        
        for i,idx in enumerate(fatjet_idx):
            print("i",i,"idx",idx)
            pt=t.FatJet_pt[idx]
            eta=t.FatJet_eta[idx]
            phi=t.FatJet_phi[idx]
            self.h1["fatjet_pt"].Fill(pt)
            self.h1["fatjet_eta"].Fill(eta)
            self.h1["fatjet_phi"].Fill(phi)
    
    def endjob(self):
        print("test_cleanedjets::endjob")
        c1 = ROOT.TCanvas("c1","test_cleanedjets",800,600)
        print("in endjob0")
        c1.Divide(2,2)
        c1.cd(1)
        s="fatjet_n"
        self.h1[s].Draw()
        c1.cd(2)
        s="fatjet_pt"
        self.h1[s].Draw()
        c1.cd(3)
        s="fatjet_eta"
        self.h1[s].Draw()
        c1.cd(4)
        s="fatjet_phi"
        self.h1[s].Draw()
        
        #  c1.Draw()  # Draw does not work here...
        c1.SaveAs("test_cleanedjets.pdf")
        #  for testing on mac
        # !open "test_cleanedjets.pdf"
        return


# In[9]:


#  for testing this helper
def main():
    nanoDir="/Users/kunori/skdir/vkk/nanoAOD/"
    nanoFile=nanoDir+"signal_M1500_0_5_18.root"
    file = ROOT.TFile.Open(nanoFile)
    tree = file.Get("Events")

    t_myphoton=test_myphoton()
    t_cleanedjets=test_cleanedjets()
   
    count=0
    for it, t in enumerate(tree):
        if it >= 100:
            break
        count=count+1
    
        t_myphoton.analyze(t)
        t_cleanedjets.analyze(t)
        genIdx=getGenIndex(t)
        print("genIdx",genIdx)
        
        a=[]
        # a=["met","genPart","recoPhoton","recoPhoton_all","recoFatjet","recoFatjet_all"]
        # a=["met","genPart","recoPhoton","recoPhoton_all","recoFatjet"]
        if it in [0,1,20,26,40]:
            print_event(it, t,a)
            
    
    # end of job
    print("***",count,"Events Processed")
    t_myphoton.endjob()
    t_cleanedjets.endjob()
    
    dothis=[0,1,20,26,40]
        # a=[]
    # a=["met","genPart","recoPhoton","recoPhoton_all","recoFatjet","recoFatjet_all"]
    # a=["met","genPart","recoPhoton","recoPhoton_all","recoFatjet"]
    # print_event(it, t,a)

    print("end of def main...")
    return 0

if __name__ == '__main__':
    main()
    print("end of test job...")


# In[ ]:




