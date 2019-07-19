# HIPLAY7 –  myelin_content

 `myelin_content_hippo.py`  – compute a myelin proxy in differents regions of the hippocampus 

**Authors** : Mathilde Ripart (Neurospin, CEA)

## Overview
`myelin_content` is a script that compute a myelin proxy in different cortical and hippocampal regions. 
First a  R1 map corrected from B1+ inhomogeneities is compute, using the information from a B1 map and the T1 uniform from the MP2RAGE sequence. 
Second, a cortical and hippocampal parcellation based on freesurfer `recon-all` is performed. This takes as input a uniform and denoised T1 contrast from the MP2RAGE sequence. 

## Getting Started

### Prerequisites
myelin_content requires the following softaware and libraries : 
- Python (version 3.7)
  - nibabel
  - numpy
  - pandas
  - scipy
  - matplotlib
  
- Freesurfer V.6
  - 1. To install freesurfer V.6 please refers to the instructions found in the following website : [Freesurfer V.6 installation](https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall)
Please, make sure to add this two lines in you default setup file (.bashrc) : 
  ```
  export FREESURFER_HOME=/neurospin/grip/protocols/MRI/HIPLAY7_mr_2019/Prog/freesurfer
  source $FREESURFER_HOME/SetUpFreeSurfer.sh
```

### Installing
- [ ] Copy the URL of the repository from GitHub
- [ ] Dive into the folder where you want to install the program. 
- [ ] Type git clone, and then paste the URL : `git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY`
- [ ] Press Enter. Your local clone will be created. 

## Usage
run `myelin_content_hippo.py [DATE_NIP] <output_path>`

with : 
```
DATE_NIP : the acquisition date in format yyyymmdd and the patient NIP. Correspond as a subject identifier.
output_path : the path to the output folder
```

Exemple : `myelin_content_hippo.py 20190719_mr331057 /home/Documents/Hiplay_results`


## References 
For any use of this code, the following paper must be cited :
> *[1] Natalia Zaretskaya et al, Advantages of cortical surface reconstruction using submillimeter 7 T MEMPRAGE, 2018, NeuroImage 165*

> *[2] JE Iglesias, A computational atlas of the hippocampal formation using ex vivo, ultra-high resolutionMRI: Application to adaptive segmentation of in vivo MRI, Neuroimage, 2015*

> *[3] A.Massire et al, High-resolution multi-parametric quantitative magnetic resonance imaging of the human cervical spinal cord at 7T, NeuroImage, 2016*
