#Module
import os
import T1map
import pandas as pd
import shutil
from T1map.Preprocess_mp2r import Dicom_to_Nifti
from T1map.B1correction import correct_from_B1
from T1map.Perform_segmentation_V2 import apply_pipeline_seg
from T1map.Myelin_content_V2 import process_results, R1_per_region
from T1map.functions import is_directory, is_file
# import importlib
# importlib.reload(T1map.Perform_segmentation_V2)
# importlib.reload(T1map.Myelin_content_V2)


#Path to directory which contains subj/t1 and subj/pd directories
acquisition_data_directory = '/neurospin/acquisition/database/Investigational_Device_7T'  # Directory where the data acquired are stored

#Path to root output directory (note: subj directories will be created as part of processing).
processed_data_directory = '/neurospin/grip/protocols/MRI/HIPLAY7_mr_2019/pipeline_test' # Directory where the processed data are stored


#-------------Initialisation -----------------------------------

#Creation of the main forlder
output_folder = processed_data_directory
error =  is_directory(processed_data_directory)

#Creation of folder for freesurfer outputs
freesurf_output_dir = os.path.join(output_folder, "freesurfer_outputs")
error =  is_directory(freesurf_output_dir)

# Copy expert file for segmentation recon-all from freesurfer
file = '/home/mr259480/PycharmProjects/HIPLAY7/T1map/expert.opts'
expert_file = os.path.join(freesurf_output_dir, 'expert.opts')
if is_file(expert_file)==0:
    shutil.copyfile(file, expert_file)


#-------------Patient information-------------------------------
# acquisition date and nip in the corresponding order.
acquisition_date_nip = pd.read_csv(os.path.join(processed_data_directory, 'patients_acq_date_nip.txt'), sep=',')
n_subjects = len(acquisition_date_nip)

#------------- Processes--------------------------------------------
    # Steps
    steps  = ['1.Inputs', '2.Data_unbiased', '3.Segmentation', '4.Results']
    steps_do = [1,1,0,0]

for subject in range(n_subjects):
    NIP = acquisition_date_nip.loc[subject]['NIP']
    date = str(acquisition_date_nip.loc[subject]['acquisition_date'])

    subj_name = date + '_' + NIP

    #----------------Create Directory-------------------------------------

    # Dive into folder subject
    print("INFO : Start processing for {}".format(subj_name))
    subject_directory = os.path.join(output_folder, subj_name)
    error =  is_directory(subject_directory)

    #-------------Load DICOM and convert in Nifti-------------------
    if steps_do[0] == 1:
        # Key word for data to load
        acquisition_identifiers = ['(.*)b1-map-xfl-sag-B1(.*)','(.*)t1-mp2rage-sag-iso0.75mm-T1-Images(.*)','(.*)t1-mp2rage-sag-iso0.75mm-UNI-Images(.*)','(.*)t1-mp2rage-sag-iso0.75mm-UNI-DEN(.*)','(.*)t1-mp2rage-sag-iso0.75mm-INV2-ND(.*)']
        acquisition_output = ['b1','t1_image','uni_images','uni-den','inv2']

        # Dive into the good folder
        folder_name = steps[0]
        folder_path = os.path.join(subject_directory, folder_name)
        error =  is_directory(folder_path)


        print("INFO : Load and convert Dicom files to Nifti files")
        error = Dicom_to_Nifti(acquisition_data_directory,folder_path,NIP,date,acquisition_identifiers,acquisition_output)
        # Preprocess inputs
        file_name = ['b1map','t1q','t1uni','t1uni_den','PDw']
        i=0
        while i <=4:
            os.rename(os.path.join(folder_path, acquisition_output[i]+'.nii.gz'), os.path.join(folder_path,file_name[i]+'.nii.gz'))
            i=i+1


    #----------- B1 correction---------------------------------------------
    if steps_do[1] == 1:
        # Dive into the good folder
        folder_name = steps[1]
        folder_path = os.path.join(subject_directory, folder_name)
        error =  is_directory(folder_path)                                #Test if directory exist or create it

        print('INFO : Starting correction from B1')
        correct_from_B1(subject_directory, steps)                         #Correct quantitative data from B1+



























































    # #------------ Segmentation  ------------------------------------------
    if steps_do[2] == 1:
        folder_name = steps[2]
        folder_path = os.path.join(subject_directory, folder_name)
        error =  is_directory(folder_path)
        print('INFO : Starting segmentation')
        apply_pipeline_seg(subject_directory, steps,freesurf_output_dir, subj_name)


    #------------ Analysis--------------------------------------------------------
    if steps_do[3] == 1:
        folder_name = steps[3]
        folder_path = os.path.join(subject_directory, folder_name)
        error =  is_directory(folder_path)
        print('INFO : Starting analysis')
        # process_results(subject_directory,steps)

        freesurfer_subj = os.path.join(freesurf_output_dir, subj_name)
        atlas = ['hippo_lh','hippo_rh','dkt']
        for i in range(len(atlas)):
            R1_per_region(subject_directory, steps, atlas[i],freesurfer_subj)

    #--------------END-----------------------------------------------------
    print("INFO : End of process {}".format(subj_name))
    print("INFO : Results can be find in {}".format(subject_directory))