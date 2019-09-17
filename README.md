# HIPLAY7 –  myelin_content

 `myelin_content`  – compute a myelin proxy (R1 value) for the grey matter and the white matter in differents regions of the hippocampus and the cortex 

## Overview
This program performs four steps and will create one folder for each step :
 1. **Inputs** : Extracts the needed inputs from the acquisition folder. Results save as nifti format (.nii)
 2. **B1_correction** : Computes a corrected R1 map from B1+ inhomogeneities, using the information from a B1 map and the uniform T1 given by the MP2RAGE sequence. Results save as nifti format (.nii)
 3. **Segmentation** : Performs a cortical and hippocampal parcellation using Freesurfer based on a uniform and denoised T1w image given by the MP2RAGE sequence. Results save as freesurfer format (.mgz).
 4. **Results** : Computes an average R1 value in each cortical and hippocampal regions. Results save as .txt files. 
  
## Getting Started

### Prerequisites

This program requires the following softwares and libraries : 
- Python (version 3.7)\
Libraries :
   - nibabel
   - scipy
   - matplotlib
   - dicom2nifti
- FSL 6.0
- Freesurfer V.6

WARNING: This program requires to have access to the folder "Acquisition" and "I2BM" of Neurospin. 

### Installation
- [ ] Open a terminal and paste the following sentence : `pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple hiplay`
Press enter. Your package will be installed. 
- [ ] Open your default setup file (.bashrc) : `gedit ~/.bashrc` 
Add the following lines in the .bashrc (do not change anything else) : 
```
export FREESURFER_HOME=/i2bm/local/freesurfer-6.0.0
source $FREESURFER_HOME/SetUpFreeSurfer.sh
```
Close the terminal
- [ ] Open a new terminal, you should see `Setting up environment for FreeSurfer/FS-FAST (and FSL)`.
Your hiplay package is ready to be used. 

## Usage
To launch the script, run \
`myelin_content <DATE_NIP> <output_path> [optional arguments]`

where : 
  - <DATE_NIP> : the acquisition date in format yyyymmdd and the patient NIP. Correspond to subject identifier
  - <output_path> : the path to the output folder
  - --noseg (optional) : use this flag if you do not want to perform cortical and hippocampal parcellations. The program will only compute the first two steps.

Exemple :\
`myelin_content 20190719_mr331057 /home/Documents/Hiplay_results --noseg` 

Notes : 
- The whole process can take up to 40h for images resolution of 0.75mm iso.
- This program has been only test for Linux users.
- For more information about the inputs/outputs data, please refers to the functions description within the python script.
- You can set up your own paths to freesurfer and fsl in the `myelin_content` script if you do not want to use the default ones.

## Authors

**Mathilde RIPART** (Neurospin, CEA)

Other contributors of the programm :  Aurélien Massire (Neurospin, CEA)

## References 
For any use of this code, the following paper must be cited :
> *[1] Natalia Zaretskaya et al, Advantages of cortical surface reconstruction using submillimeter 7 T MEMPRAGE, 2018, NeuroImage 165*

> *[2] JE Iglesias, A computational atlas of the hippocampal formation using ex vivo, ultra-high resolutionMRI: Application to adaptive segmentation of in vivo MRI, Neuroimage, 2015*

> *[3] A.Massire et al, High-resolution multi-parametric quantitative magnetic resonance imaging of the human cervical spinal cord at 7T, NeuroImage, 2016*

> *[4] M.Jenkinson et al, Improved Optimisation for the Robust and Accurate Linear Registration and Motion Correction of Brain Images, NeuroImage, 2002* 
