""" script to compute a myelin proxy (R1 values) in differents regions of the cortex and hippocampus

This code was developped by Mathilde Ripart at Neurospin (2019)

For any use of this code, the following paper must be cited:
[1] Natalia Zaretskaya et al, Advantages of cortical surface reconstruction using submillimeter 7 T MEMPRAGE, 2018, NeuroImage 165
[2] JE Iglesias, A computational atlas of the hippocampal formation using ex vivo, ultra-high resolutionMRI: Application to adaptive segmentation of in vivo MRI, Neuroimage, 2015
[3] A.Massire et al, High-resolution multi-parametric quantitative magnetic resonance imaging of the human cervical spinal cord at 7T, NeuroImage, 2016


"""

#------- Module & functions ------------------------------------
import os
import shutil
import io
import contextlib
import argparse
from Modules.Preprocess_mp2r import apply_processInput
from Modules.B1correction import apply_B1correction
from Modules.Perform_segmentation import apply_segmentation
from Modules.Myelin_content import apply_processResults
# import importlib
# importlib.reload(T1map.Perform_segmentation_V2)


def get_path():
#    -------------------SET UP PATHS HERE -------------------------------------------------------------
    # Path to project directory
    project_directory = os.path.dirname(os.path.realpath('Pipeline_main.py'))

    # Path to directory which contains all the acquisitions in dicom data
    deviceSeptT_directory = "/neurospin/acquisition/database/Investigational_Device_7T"

    # Path to freesurfer Home
    freesurferHome = "/neurospin/grip/protocols/MRI/HIPLAY7_mr_2019/Prog/freesurfer"

    return project_directory, deviceSeptT_directory, freesurferHome



def read_cli_args():
    """Read command-line interface arguments

    Parse the input to the command line with the argparse module.

    Args:
        N/A

    Returns:
        args (argparse.Namespace): parsed arguments
        cli_usage (string): command-line interface usage message
    """
    # read command line arguments
    cli_description = 'script to compute a myelin proxy (R1 values) in differents regions of the cortex and hippocampus'
    parser = argparse.ArgumentParser(description=cli_description)
    # add arguments
    #-- mandatory arguments
    #---- Patient identifier
    parser.add_argument(
        'date_NIP',
        metavar='date_NIP',
        help='format yyyymmdd_xxxxxxxx')
    #---- output dir
    parser.add_argument(
        'outdir_path',
        metavar='out_dir',
        help='path where output files will be stored')
    # # ---- steps to do
    # parser.add_argument(
    #     'step_todo',
    #     metavar='step_todo',
    #     help='the steps to perform : 1 = perform ; 0 = avoid')
    #-- optional arguments
    parser.add_argument(
        '--noseg',
        action="store_true",
        help='do not perform cortical and hippocampal parcellations')
    # parse all arguments
    args = parser.parse_args()

    # store usage message in string
    cli_usage = None
    with io.StringIO() as buf, contextlib.redirect_stdout(buf):
        parser.print_usage()
        cli_usage = buf.getvalue()
    if cli_usage is None:
        raise ValueError('the CLI usage variable must not be empty')

    return args, cli_usage


def main():
    '''
    myelin_content_hippo code : main function

    Takes the following inputs :
        - DATE : date (yyyymmdd) of the patient acquisition
        - NIP : nip of the patient acquisition
        - outdir_path : path to folder where results will be stored
        - steps :

    Will output the following file in differents folders in the output directory
        1.Inputs
            t1uni.nii.gz : T1 uniform image from the MP2RAGE sequence
            b1map.nii.gz : b1 map obtain from the xfl sequence
            info_uni-den : one dicom image of the T1 uniform image (to extract header information)
            info_b1 : one dicom image of the b1 map (to extract header information)
        2.B1correction
            b1_to_mp2r.nii.gz : b1map resampled at the T1 mp2rage resolution
            t1q_cor.nii : T1 map corrected from the B1+
            R1q_cor.nii : R1 map corrected from the B1+
            t1uni_cor.nii : T1 uni corrected from the B1+
        3. Segmentation

        4. Results
            seg_DKT_orig.mgz : segmentation image (desikan-kiliany labels) in the R1 original space
            seg_hippo_lh_orig.mgz : segmentation image (left hippocampus labels) in the R1 original space
            seg_hippo_rh_orig.mgz : segmentation image (right hippocampus labels) in the R1 original space
            R1_per_regions_dkt.txt : statistics on R1 values for different regions of the desikan-kiliany atlas
            R1_per_regions_hippo_lh.txt : statistics on R1 values for different regions of the left hippocampus
            R1_per_regions_hippo_rh.txt : statistics on R1 values for different regions of the right hippocampus

    '''


    # ------------ Global variable ----------------------------------

    project_directory,deviceSeptT_directory, freesurferHome = get_path()

    # parse command-line arguments
    args, cli_usage = read_cli_args()

    date_NIP = args.date_NIP
    processed_data_directory = args.outdir_path

    date = date_NIP.split('_')[0]
    NIP = date_NIP.split('_')[1]

    subj_name = date + '_' + NIP
    steps = ['1.Inputs', '2.B1correction', '3.Segmentation', '4.Myelin_proxy']

    #------------- Initialisation main output folder & subject folder -----------------------------------

    # Check if main directory exists. If not create it
    output_folder = processed_data_directory
    if os.path.isdir(output_folder):
        print('INFO : Dive into the main output folder : {} '.format(output_folder))
    else:
        print('INFO : Create the main output folder : {} '.format(output_folder))
        os.makedirs(output_folder)

    #Check if freesurfer output directory exists. If not create it.
    freesurf_output_dir = os.path.join(output_folder, "freesurfer_outputs")
    if os.path.isdir(freesurf_output_dir):
        print('INFO : Freesurfer output folder present : {} '.format(freesurf_output_dir))
    else:
        print('INFO : Create the freesurfer output folder : {} '.format(freesurf_output_dir))
        os.makedirs(freesurf_output_dir)

    # Check if expert.opts exists in freesurfer output directory. If not copy it from the project folder.
    expert_path =  os.path.join(project_directory,'expert.opts')
    expert_newpath = os.path.join(freesurf_output_dir, 'expert.opts')
    if not os.path.isfile(expert_newpath):
        shutil.copyfile(expert_path, expert_newpath)

    #Check if subject folder already exists. If yes dive into, if not create it.
    subject_directory = os.path.join(output_folder, subj_name)
    if os.path.isdir(subject_directory):
        print('INFO : Dive into the subject output folder : {} '.format(subject_directory))
    else:
        print('INFO : Create subject folder : {} '.format(subject_directory))
        os.makedirs(subject_directory)

    # Dive into folder subject
    print("INFO : Start processing for {}".format(subj_name))


    #-------------1. Load DICOM and convert in Nifti-------------------
    # Check if 1.Inputs directory already exist. If not create it.
    folder_name = steps[0]
    folder_path = os.path.join(subject_directory, folder_name)
    if os.path.isdir(folder_path):
        print('WARNING: folder {} already exist. Data are overwritten'.format(folder_name))
    else:
        os.makedirs(folder_path)

    print("INFO : Start processing the input data : Loading and convert Dicom files to Nifti files")
    apply_processInput(deviceSeptT_directory, folder_path, NIP, date)

    del folder_path, folder_name

    #----------- 2. B1 correction---------------------------------------------

    # Check if 2.B1correction already exist. If not create it.
    folder_name = steps[1]
    folder_path = os.path.join(subject_directory, folder_name)
    if os.path.isdir(folder_path):
        print('WARNING: folder {} already exist. Data are overwritten'.format(folder_name))
    else:
        os.makedirs(folder_path)

    print('INFO : Starting correction from B1')
    apply_B1correction(subject_directory, steps,  project_directory)

    del folder_path, folder_name


    # #------------ 3. Segmentation  ------------------------------------------
    if args.noseg:
        # Check if 3.Segmentation already exist. If not create it.
        folder_name = steps[2]
        folder_path = os.path.join(subject_directory, folder_name)
        if os.path.isdir(folder_path):
            print('WARNING: folder {} already exist. Data are overwritten'.format(folder_name))
        else:
            os.makedirs(folder_path)

        print('INFO : Start segmentation process')
        apply_segmentation(subject_directory, steps,freesurf_output_dir, subj_name)


    #------------ 4. Analysis--------------------------------------------------------
        # Check if 4.Myelin_proxy already exist. If not create it. < 5
        folder_name = steps[3]
        folder_path = os.path.join(subject_directory, folder_name)
        if os.path.isdir(folder_path):
            print('WARNING: folder {} already exist. Data are overwritten'.format(folder_name))
        else:
            os.makedirs(folder_path)

        print('INFO : Start processing the results : compute R1 value in different ROI')
        apply_processResults(subject_directory, steps,freesurf_output_dir, subj_name, freesurferHome)


    #--------------END-----------------------------------------------------

    print("INFO : End of process for {}".format(subj_name))
    print("INFO : Results can be find in {}".format(subject_directory))

if __name__ == "__main__":
    main()
