import subprocess
import shutil
import os
import re
import warnings


def Dicom_to_Nifti(deviceSeptT_directory, acquisition_output_directory, NIP, date, acquisition_identifiers,
                   acquisition_output):
    # Download dicom images from a MRI scanner database, based on regular
    # expression to search the right folder + Copy in the output directory one dicom image per dicom folder


    # Locate the acquisition data folder and dive into the corresponding nip
    subject_acquisition_date_directory = os.path.join(deviceSeptT_directory, date)
    # List the corresponding folders
    acquisition_date_folder_list = os.listdir(subject_acquisition_date_directory)
    # Find the subject folder based on NIP
    nip_pattern = re.compile('{}(.*)'.format(NIP))
    matching_nip_folders = \
        [nip_pattern.search(f).group() for f in acquisition_date_folder_list
         if nip_pattern.search(f) is not None]
    if len(matching_nip_folders) == 1:
        # Dive into the subject directory
        subject_dicom = os.path.join(deviceSeptT_directory, date, matching_nip_folders[0])
        subject_dicom_list = os.listdir(subject_dicom)
        # Loop over the different acquisition we want to fetch
        for acq in range(len(acquisition_identifiers)):
            # Find the folder corresponding to the current identifiers
            acq_pattern = re.compile('{}'.format(acquisition_identifiers[acq]))
            matching_acquisition_folders = \
                [acq_pattern.search(f).group() for f in subject_dicom_list
                 if acq_pattern.search(f) is not None]
            # If two or more matching pattern are found, take the first one
            # by defaults and raise a warning
            if len(matching_acquisition_folders) >= 2:
                warnings.warn('Careful! \n Find {} acquisitions folders matching you\'re request: {}. Taking '
                              'the first one.'.format(len(matching_acquisition_folders), matching_acquisition_folders))
                matching_acquisition_folder = matching_acquisition_folders[0]
            else:
                matching_acquisition_folder = matching_acquisition_folders[0]

            # Dive into the right dicom folder for the right folder
            subject_dicom_images = os.path.join(subject_dicom, matching_acquisition_folder)

            # # Copy all dicom image in the chosen root directory with the chosen
            #     # subtree architecture
            subprocess.call('dicom2nifti {} {}'.format(subject_dicom_images, acquisition_output_directory),
                                shell=True)
            #
            # # List the files in the output folder
            filename_list = os.listdir(acquisition_output_directory)
            contrast_pattern = re.compile('(.*){}(.*)'.format(acquisition_output[acq]))
            filename = [contrast_pattern.search(f).group() for f in filename_list if contrast_pattern.search(f) is not None]
            # New file name
            filename_output = os.path.join(acquisition_output_directory, acquisition_output[acq] + '.nii.gz')
            # rename the file
            os.rename(os.path.join(acquisition_output_directory, filename[0]), filename_output)

            # Copy one dcm image
            dcm_list = os.listdir(subject_dicom_images)
            file = os.path.join(subject_dicom_images,dcm_list[1])
            copy_file = os.path.join(acquisition_output_directory,'info_'+ acquisition_output[acq])
            shutil.copyfile(file,copy_file)

    print("INFO : End of data preprocess")