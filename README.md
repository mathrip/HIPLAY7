# HIPLAY7 –  myelin_content

 `myelin_content_hippo.py`  – compute a myelin proxy in differents regions of the hippocampus 

**Authors** : Mathilde Ripart (Neurospin, CEA)

## Overview
`myelin_content_hippo` is a script that reconstruct a corrected R1 map and perform a cortical and hippocampal parcellation from the following inputs :
- B1 map
- T1 uniform denoised from the MP2RAGE sequence

## Installation
myelin_content requires the following softaware and libraries : 
- Python (version 3.7)
  - nibabel
  - numpy
  - pandas
  - scipy
  - matplotlib
  
- Freesurfer V.6
  need to add in the bashrc the path to set up the Freesurfer Environment :
  ```
  export FREESURFER_HOME=/neurospin/grip/protocols/MRI/HIPLAY7_mr_2019/Prog/freesurfer
  source $FREESURFER_HOME/SetUpFreeSurfer.sh
  ```
## Usage
To launch `myelin_content_hippo.py`


## References 
> *[1] Natalia Zaretskaya et al, Advantages of cortical surface reconstruction using submillimeter 7 T MEMPRAGE, 2018, NeuroImage 165*

> *[2] JE Iglesias, A computational atlas of the hippocampal formation using ex vivo, ultra-high resolutionMRI: Application to adaptive segmentation of in vivo MRI, Neuroimage, 2015*

> *[3] A.Massire et al, High-resolution multi-parametric quantitative magnetic resonance imaging of the human cervical spinal cord at 7T, NeuroImage, 2016*
