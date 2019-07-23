import subprocess
import shutil
import os
import re
import warnings


def apply_processInput(acquisition_output_directory, inputs_path):
    """
    Download dicom images from a MRI scanner database, based on regular
    expression to search the right folder + Copy in the output directory one dicom image per dicom folder

    Parameters
    ----------
        acquisition_output_directory : string
            path to the output directory where the nifti data are saved
        inputs_path  : list of strings
            name of the dicom folder of the acquisition b1map, T1map, T1 uniform and T1 uniform denoised

    Outputs
    ---------
    the following outputs are saved in the 1.Inputs folder:
            t1uni.nii.gz : T1 uniform image from the MP2RAGE sequence
            t1uni_den.nii.gz : T1 uniform and denoised image from the MP2RAGE sequence
            b1map.nii.gz : b1 map obtain from the xfl sequence
            info_uni : one dicom image of the T1 uniform image (to extract header information)
            info_uni-den : one dicom image of the T1 uniform and denoised image (to extract header information)
            info_b1 : one dicom image of the b1 map (to extract header information)
     """

    #------------------ SET UP IDENTIFIERS------------------------------------------------------------------------
    acquisition_nifti_identifiers = ['b1', 't1_image', 'uni_images', 'uni-den']
    output_files_names = ['b1map', 't1q', 't1uni', 't1uni_den']



    #-----------------PROCESS--------------------------------------------------------------------------------------

    # Loop over the different acquisition we want to fetch
    for acq in range(len(inputs_path)):

        # Dive into the right dicom folder for the right folder
        subject_dicom_images = inputs_path[acq]

        # # Copy all dicom image in the chosen root directory with the chosen
        #     # subtree architecture
        subprocess.call('dicom2nifti {} {}'.format(subject_dicom_images, acquisition_output_directory),
                            shell=True)

        # # List the files in the output folder
        filename_list = os.listdir(acquisition_output_directory)
        contrast_pattern = re.compile('(.*){}(.*)'.format(acquisition_nifti_identifiers[acq]))
        filename = [contrast_pattern.search(f).group() for f in filename_list if contrast_pattern.search(f) is not None]
        # New file name
        filename_output = os.path.join(acquisition_output_directory, acquisition_nifti_identifiers[acq] + '.nii.gz')
        # rename the file
        os.rename(os.path.join(acquisition_output_directory, filename[0]), filename_output)

        # Copy one dcm image
        dcm_list = os.listdir(subject_dicom_images)
        file = os.path.join(subject_dicom_images,dcm_list[1])
        copy_file = os.path.join(acquisition_output_directory,'info_'+ acquisition_nifti_identifiers[acq])
        shutil.copyfile(file,copy_file)

        # Set new files name
        os.rename(os.path.join(acquisition_output_directory, acquisition_nifti_identifiers[acq] + '.nii.gz'),
                  os.path.join(acquisition_output_directory, output_files_names[acq] + '.nii.gz'))

    print("INFO : End of first part")
