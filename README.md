# HIPLAY7 –  myelin_content

 `myelin_content.py`  – compute a myelin proxy based on R1 value in differents regions of the hippocampus and the cortex

**Authors** : Mathilde Ripart (Neurospin, CEA)

## Overview
This program perform four steps and will create one folder for each step :
 1. **Inputs** : Extract the needed inputs from the acquisition folder. Results save as nifti format (.nii)
 2. **B1correction** : Compute a corrected R1 map from B1+ inhomogeneities, using the information from a B1 map and the uniform T1 given by the MP2RAGE sequence. Results save as nifti format (.nii)
 3. **Segmentation** : Perform a cortical and hippocampal parcellation using Freesurfer based on a uniform and denoised T1 image given by the MP2RAGE sequence. Results save as  freesurfer format (.mgz)
 4. **Results** : Compute the average R1 value in each cortical and hippocampal regions. Results save as .txt files. 
  
## Getting Started

### Prerequisites

This program requires the following softwares and libraries : 
- Python (version 3.7)\
To install Python 3.7 you can download the [anaconda distribution](https://www.anaconda.com/distribution/#linux) and follow the [instructions](https://docs.anaconda.com/anaconda/install/linux/)\
To install a python library, use the following command : `pip install LibraryName`\
Libraries :   
  - nibabel
  - numpy
  - pandas
  - scipy
  - matplotlib

- Freesurfer V.6\
To install freesurfer V.6 please refers to the instructions found in the following website : [Freesurfer V.6 installation](https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall)\
Please, make sure to add this two lines in you default setup file (.bashrc) : 
```
  export FREESURFER_HOME=/neurospin/grip/protocols/MRI/HIPLAY7_mr_2019/Prog/freesurfer
  source $FREESURFER_HOME/SetUpFreeSurfer.sh
```

Note : This program has been test only by Linux users.

### Installation
- [ ] Copy the URL of the repository from GitHub
- [ ] Dive into the folder where you want to install the program. 
- [ ] Type git clone, and then paste the URL : `git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY`
- [ ] Press Enter. Your local clone will be created. 

## Usage
run `myelin_content_hippo.py [DATE_NIP] [output_path]`

where : 
- [DATE_NIP] : the acquisition date in format yyyymmdd and the patient NIP. Correspond to subject identifier
- [output_path] : the path to the output folder

Exemple : `myelin_content_hippo.py 20190719_mr331057 /home/Documents/Hiplay_results`

Notes : for more information about the inputs and the outputs data, please refers to each function description within the python script. 
 
## References 
For any use of this code, the following paper must be cited :
> *[1] Natalia Zaretskaya et al, Advantages of cortical surface reconstruction using submillimeter 7 T MEMPRAGE, 2018, NeuroImage 165*

> *[2] JE Iglesias, A computational atlas of the hippocampal formation using ex vivo, ultra-high resolutionMRI: Application to adaptive segmentation of in vivo MRI, Neuroimage, 2015*

> *[3] A.Massire et al, High-resolution multi-parametric quantitative magnetic resonance imaging of the human cervical spinal cord at 7T, NeuroImage, 2016*
