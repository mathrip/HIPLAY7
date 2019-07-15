#Module
import os
import T1map
from T1map.Preprocess_mp2r import Dicom_to_Nifti
from T1map.B1correction import correct_from_B1
from T1map.Perform_segmentation import apply_pipeline_seg
from T1map.Myelin_content import process_results, R1_per_tissu, R1_per_region

import importlib
importlib.reload(T1map.B1correction)
importlib.reload(T1map.Myelin_content)

import T1map
#functions
def is_directory(directory_path):
    if os.path.exists(directory_path):
        exist = 1
        print('INFO : Directory {} already exists'.format(directory_path))
    else:
        exist = 0
        os.makedirs(directory_path)
    return exist


def is_file(file_path):
    if os.path.exists(file_path):
        exist = 1
        print('INFO : File {} already exist. Use existing file for the ratio'.format(file_path))
    else:
        exist = 0
        print('WARNINGFile {} does not exist'.format(file_path))
    return exist

#Path to directory which contains subj/t1 and subj/pd directories
acquisition_data_directory = '/neurospin/acquisition/database/Investigational_Device_7T'  # Directory where the data acquired are stored

#Path to root output directory (note: subj directories will be created as part of processing).
processed_data_directory = '/neurospin/grip/protocols/MRI/HIPLAY7_mr_2019/Controls' # Directory where the processed data are stored

#-------------Patient information-------------------------------
NIP = 'md130174'
date ='20190619'


#----------------Create Directory-------------------------------------

# Dive into folder subject
subject_directory = os.path.join(processed_data_directory,date+'_'+NIP)
error =  is_directory(subject_directory)

# Steps :
steps  = ['1.Inputs', '2.B0_correction', '3.Segmentation', '4.qMyelin']
#-------------Load DICOM and convert in Nifti-------------------

# Key word for data to load
acquisition_identifiers = ['(.*)b1-map-xfl-sag-B1(.*)','(.*)t1-mp2rage-sag-iso0.75mm-T1-Images(.*)','(.*)t1-mp2rage-sag-iso0.75mm-UNI-Images(.*)','(.*)t1-mp2rage-sag-iso0.75mm-UNI-DEN(.*)','(.*)t1-mp2rage-sag-iso0.75mm-INV2-ND(.*)']
acquisition_output = ['b1','t1_image','uni_images','uni-den','inv2']

# Dive into the good folder
folder_name = steps[0]
folder_path = os.path.join(subject_directory, folder_name)
error =  is_directory(folder_path)


print("INFO : LOad and convert Dicom files to Nifti files")
error = Dicom_to_Nifti(acquisition_data_directory,folder_path,NIP,date,acquisition_identifiers,acquisition_output)
# Preprocess inputs
file_name = ['b1map','t1q','t1uni','t1uni_den','PDw']
i=0
while i <=4:
    os.rename(os.path.join(folder_path, acquisition_output[i]+'.nii.gz'), os.path.join(folder_path,file_name[i]+'.nii.gz'))
    i=i+1


#----------- B1 correction---------------------------------------------
# Dive into the good folder
folder_name = steps[1]
folder_path = os.path.join(subject_directory, folder_name)
error =  is_directory(folder_path)
print('INFO : Starting correction from B1')
correct_from_B1(subject_directory, steps)

#------------ Segmentation  ------------------------------------------
folder_name = steps[2]
folder_path = os.path.join(subject_directory, folder_name)
error =  is_directory(folder_path)
print('INFO : Starting segmentation')
apply_pipeline_seg(subject_directory, steps)

#------------ R1 map & stats --------------------------------------------------------
folder_name = steps[3]
folder_path = os.path.join(subject_directory, folder_name)
error =  is_directory(folder_path)
print('INFO : Starting analysis')
process_results(subject_directory,steps)

R1_per_tissu(subject_directory, steps)
R1_per_region(subject_directory, steps)

#--------------END-----------------------------------------------------
print("INFO : End of pipeline ")
print("INFO : Results can be find in {}".format(subject_directory))