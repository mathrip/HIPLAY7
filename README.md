# HIPLAY7 –  myelin_content

 `myelin_content.py`  – compute a myelin proxy (R1 value) for the grey matter and the white matter in differents regions of the hippocampus and the cortex 

## Overview
This program performs four steps and will create one folder for each step :
 1. **Inputs** : Extracts the needed inputs from the acquisition folder. Results save as nifti format (.nii)
 2. **B1correction** : Computes a corrected R1 map from B1+ inhomogeneities, using the information from a B1 map and the uniform T1 given by the MP2RAGE sequence. Results save as nifti format (.nii)
 3. **Segmentation** : Performs a cortical and hippocampal parcellation using Freesurfer based on a uniform and denoised T1w image given by the MP2RAGE sequence. Results save as freesurfer format (.mgz)
 4. **Results** : Computes an average R1 value in each cortical and hippocampal regions. Results save as .txt files. 
  
## Getting Started

### Prerequisites

This program requires the following softwares and libraries : 
- Python (version 3.7)\
Libraries :
   - nibabel
   - numpy
   - pandas
   - scipy
   - matplotlib\
If you do not have Python installed, we recommend to install Python 3.7 from the [anaconda distribution](https://www.anaconda.com/distribution/#linux) and to follow the [instructions](https://docs.anaconda.com/anaconda/install/linux/)\
Each library can be then install using the following command : `pip install LibraryName`\

- FSL 6.0
To install FSL 6.0 please refers to the instructions found in the following website : [FslInstallation](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation/Linux)\
Please, make sure to add this two lines in you default setup file (.bashrc) : 
```
FSLDIR=pathWhereFSLHasBeenStored
. ${FSLDIR}/etc/fslconf/fsl.sh
PATH=${FSLDIR}/bin:${PATH}
export FSLDIR PATH
```

- Freesurfer V.6\
To install freesurfer V.6 please refers to the instructions found in the following website : [Freesurfer V.6 installation](https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall)\
Please, make sure to add this two lines in you default setup file (.bashrc) : 
```
  export FREESURFER_HOME= pathWhereFreesurferHasBeenStored
  source $FREESURFER_HOME/SetUpFreeSurfer.sh
```

### Installation
- [ ] Copy the URL of the repository from GitHub
- [ ] Dive into the folder where you want to store the program and open a terminal
- [ ] Type git clone, and then paste the URL : `git clone https://github.com/USERNAME/REPOSITORY`
- [ ] Press Enter. Your local clone will be created

## Usage
 :heavy_exclamation_mark: Before to run the program, make sure to update the following path in the myelin_content.py script : \
*deviceSept_directory* : which is the directory where all the acquisition are stored with a defined architecture\
*freesurferHome* : which is the path where freesurfer has been stored.

To launch the recombine.py script, run \
`python myelin_content_hippo.py <DATE_NIP> <output_path> [optional arguments]`

where : 
  - <DATE_NIP> : the acquisition date in format yyyymmdd and the patient NIP. Correspond to subject identifier
  - <output_path> : the path to the output folder
  - --noseg (optional) : use this flag if you do not want to perform cortical and hippocampal parcellations. The program will only compute the first two steps. 

Exemple :\
`myelin_content_hippo.py 20190719_mr331057 /home/Documents/Hiplay_results --noseg` 

Notes : 
- The whole process can take up to 40h for images resolution of 0.75mm iso.
- This program has been only test for Linux users.
- For more information about the inputs/outputs data, please refers to the functions description within the python script.

## Authors

**Mathilde RIPART** (Neurospin, CEA)

Other contributors of the programm :  Aurélien Massire (Neurospin, CEA)

## References 
For any use of this code, the following paper must be cited :
> *[1] Natalia Zaretskaya et al, Advantages of cortical surface reconstruction using submillimeter 7 T MEMPRAGE, 2018, NeuroImage 165*

> *[2] JE Iglesias, A computational atlas of the hippocampal formation using ex vivo, ultra-high resolutionMRI: Application to adaptive segmentation of in vivo MRI, Neuroimage, 2015*

> *[3] A.Massire et al, High-resolution multi-parametric quantitative magnetic resonance imaging of the human cervical spinal cord at 7T, NeuroImage, 2016*

> *[4] M.Jenkinson et al, Improved Optimisation for the Robust and Accurate Linear Registration and Motion Correction of Brain Images, NeuroImage, 2002* 
