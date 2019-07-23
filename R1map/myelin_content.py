""" script to compute a myelin proxy (R1 values) in differents regions of the cortex and hippocampus

This code was developped by Mathilde Ripart at Neurospin (2019)

For any use of this code, the following paper must be cited:
[1] Natalia Zaretskaya et al, Advantages of cortical surface reconstruction using submillimeter 7 T MEMPRAGE, 2018, NeuroImage 165
[2] JE Iglesias, A computational atlas of the hippocampal formation using ex vivo, ultra-high resolutionMRI: Application to adaptive segmentation of in vivo MRI, Neuroimage, 2015
[3] A.Massire et al, High-resolution multi-parametric quantitative magnetic resonance imaging of the human cervical spinal cord at 7T, NeuroImage, 2016
[4] M.Jenkinson et al, Improved Optimisation for the Robust and Accurate Linear Registration and Motion Correction of Brain Images, NeuroImage, 2002

"""

#Module & functions
import os
import shutil
import io
import contextlib
import argparse
from Modules.Preprocess_mp2r import apply_processInput
from Modules.B1correction import apply_B1correction
from Modules.Perform_segmentation import apply_segmentation
from Modules.Compute_results import apply_processResults
# import importlib
# importlib.reload(T1map.Perform_segmentation_V2)


#    -------------------SET UP PATHS HERE -------------------------------------------------------------
def get_path():
    # Path to project directory
    project_directory = os.path.dirname(os.path.realpath('myelin_content.py'))

    # Path to directory which contains all the acquisitions in dicom data
    deviceSeptT_directory = "/neurospin/acquisition/database/Investigational_Device_7T"

    # Path to freesurfer Home
    freesurferHome = "/neurospin/grip/protocols/MRI/HIPLAY7_mr_2019/Prog/freesurfer"

    return project_directory, deviceSeptT_directory, freesurferHome

#--------------------------------------------------------------------------------------------------------

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
    main script of the myelin_content program.
    The program first performs a R1map (myelin proxy) corrected from B1+ inhomogeneities based on the uniform T1 contrast from the mp2rage sequence and a b1map.
    A cortical and hippocampal parcellation are performed using freesurfer, and the R1 values are quantified in the differents ROIs. This part is optional.

    Parameters
    ----------
        <Date_NIP> : date (format yyyymmdd) & NIP of the patient acquisition
        <outdir_path> : path to folder in which results will be stored
        --noseg (OPTIONAL) : do not perform cortical and hippocampal parcellations

    Outputs
    ----------
    Will output the following file in four differents folders in the output directory :
        1.Inputs
            t1q.nii.gz : T1 map image from the MP2RAGE sequence
            t1uni.nii.gz : T1 uniform image from the MP2RAGE sequence
            t1uni_den.nii.gz : T1 uniform and denoised image from the MP2RAGE sequence
            b1map.nii.gz : b1 map obtain from the xfl sequence
            info_t1_image : one dicom image of the T1 map (to extract header information)
            info_uni : one dicom image of the T1 uniform image (to extract header information)
            info_uni-den : one dicom image of the T1 uniform and denoised image (to extract header information)
            info_b1 : one dicom image of the b1 map (to extract header information)
        2.B1correction
            b1_to_mp2r.nii.gz : b1map resampled at the T1 mp2rage resolution
            t1q_cor.nii : T1 map corrected from the B1+
            R1q_cor.nii : R1 map corrected from the B1+
            (optional) t1uni_cor.nii : T1 uni corrected from the B1+
        3. Segmentation
            brainmask_orig.mgz : brain mask in the T1 original space
            seg_DKT_orig.mgz : cortical parcellation volume (desikan-kiliany labels) in the T1 original space
            seg_hippo_lh_orig.mgz : hippocampal parcellation volume (left hippocampus labels) in the T1 original space
            seg_hippo_rh_orig.mgz : hippocampal parcellation volume (right hippocampus labels) in the T1 original space
        4. Results
            t1q_cor_clean.nii.gz : T1 map corrected and skull-stripped
            R1q_cor_clean.nii.gz : R1 map corrected and skull-stripped
            R1_per_regions_dkt.txt : statistics on R1 values for different regions of the desikan-kiliany atlas
            R1_per_regions_hippo_lh.txt : statistics on R1 values for different regions of the left hippocampus
            R1_per_regions_hippo_rh.txt : statistics on R1 values for different regions of the right hippocampus

    '''




    #------------- Initialisation main output folder & subject folder -----------------------------------

    project_directory, deviceSeptT_directory, freesurferHome = get_path()

    # parse command-line arguments
    args, cli_usage = read_cli_args()

    date_NIP = args.date_NIP
    date = date_NIP.split('_')[0]
    NIP = date_NIP.split('_')[1]
    subj_name = date + '_' + NIP

    processed_data_directory = args.outdir_path

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

    # Start steps
    steps = ['1.Inputs', '2.B1correction', '3.Segmentation', '4.Myelin_proxy']

    #-------------1. Load DICOM and convert in Nifti-------------------

    # Check if 1.Inputs directory already exist. If not create it.
    folder_name = steps[0]
    folder_path = os.path.join(subject_directory, folder_name)
    if os.path.isdir(folder_path):
        print('WARNING: folder {} already exist. Data are overwritten'.format(folder_name))
    else:
        os.makedirs(folder_path)
        
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
        
    apply_B1correction(subject_directory, steps,  project_directory)

    del folder_path, folder_name

    # #------------ 3. Segmentation  ------------------------------------------

    if not args.noseg:
        # Check if 3.Segmentation already exist. If not create it.
        folder_name = steps[2]
        folder_path = os.path.join(subject_directory, folder_name)
        if os.path.isdir(folder_path):
            print('WARNING: folder {} already exist. Data are overwritten'.format(folder_name))
        else:
            os.makedirs(folder_path)
          
        apply_segmentation(subject_directory, steps,freesurf_output_dir, subj_name)
        
        del folder_path, folder_name
        

    #------------ 4. Analysis--------------------------------------------------------

        # Check if 4.Myelin_proxy already exist. If not create it. < 5
        folder_name = steps[3]
        folder_path = os.path.join(subject_directory, folder_name)
        if os.path.isdir(folder_path):
            print('WARNING: folder {} already exist. Data are overwritten'.format(folder_name))
        else:
            os.makedirs(folder_path)
  
        apply_processResults(subject_directory, steps,freesurf_output_dir, subj_name, freesurferHome)


    #--------------END-----------------------------------------------------
    print("INFO : End of process. Results for {} can be find in {}".format(subj_name,subject_directory))

if __name__ == "__main__":
    main()
