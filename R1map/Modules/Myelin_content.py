import os

def apply_mask(path_input, mask, path_output):
    """
    Apply binary mask to an image using the function fslmaths from FSL

    Parameters
    ----------
    path_input : string
        path of the image (in .nii or .nii.gz) to apply the mask on
    mask : string
        path to the binary mask in .nii or .nii.gz
    path_output : string
        the path of the folder on which to save the output on
    """
    from subprocess import Popen, PIPE
    fslmaths = ["fslmaths",
                "{}".format(path_input),
                "-mul", "{}".format(mask),
                "{}".format(path_output)]
    fslmaths_cmd = Popen(fslmaths, stdout=PIPE)
    fslmaths_output, fslmaths_error = fslmaths_cmd.communicate()
    return fslmaths_output, fslmaths_error

def orig_space(path_input, path_ref, path_output):
    """
    Perform a coregistration the freesurfer output to the original space of the image using
    the function mriconvert from FreeSurfer

    Parameters
    ----------
    path_input : string
        path of the image (.mgz) to apply register
    path_ref : string
        path to the freesurfer recon-all output "mri/rawavg.mgz" to use as a reference
    path_output : string
        path to save the image (.mgz) in its original space

    """
    from subprocess import Popen, PIPE
    mriconvert = ["mri_convert",
                  "-rt", "nearest",
                  "-rl", "{}".format(path_ref),
                  "{}".format(path_input),
                  "{}".format(path_output)]
    mriconvert_cmd = Popen(mriconvert, stdout=PIPE)
    mriconvert_output, mriconvert_error = mriconvert_cmd.communicate()
    return mriconvert_output, mriconvert_error

def stats_in_file(path_input, labels3D, path_output,freesurferHome):
    """
    Compute the statistics (means and standard deviation) of pixels intensity in different region of an atlas

    Parameters
    ----------
    path_input : string
        path of the image (in .nii or .nii.gz) to compute the intensity value statistics on
    labels3D : string
        path of the image that contains the labels of the atlas (.mgz)
    path_output : string
        the path of the folder on which to save the output on
    freesurferHome : string
        path of the freesurfer installation folder on which to find the file 'FreeSurferColorLUT.txt'

    """
    from subprocess import Popen, PIPE
    color_labels = os.path.join(freesurferHome,'FreeSurferColorLUT.txt')
    mrisegstats = ["mri_segstats",
                  "--seg", "{}".format(labels3D),
                  "--sum", "{}".format(path_output),
                  "--i","{}".format(path_input),
                  "--ctab","{}".format(color_labels)]
    mrisegstats_cmd = Popen(mrisegstats, stdout=PIPE)
    mrisegstats_output, mrisegstats_error = mrisegstats_cmd.communicate()
    return mrisegstats_output, mrisegstats_error

def R1_per_region(path_directory, steps, atlas, freesurfer_subj, freesurferHome):
    """
    Compute the R1 values in different region of the cortex (desikan-kiliany atlas) and hippocampus

    Parameters
    ----------
    path_directory : string
        the path where all the pipeline results are stored, Should correspond to "processed_data_directory"
    steps : list of strings
      list containing the name of the steps performed on the pipeline
    atlas : string
     name of the atlas to use for the parcelation
    freesurfer_subj : string
        path of the subject directory in the freesurfer subject directory

    """

    # Regis template to original space
    if atlas == 'dkt':
        input_name = 'mri/aparc.DKTatlas+aseg.mgz'         #for DKT atlas
        output_name = 'seg_DKT_orig.mgz'
    elif atlas == 'hippo_lh':
        input_name = 'mri/lh.hippoSfLabels-T1.v10.mgz'  # for DKT atlas
        output_name = 'seg_hippo_lh_orig.mgz'
    elif atlas == 'hippo_rh':
        input_name = 'mri/rh.hippoSfLabels-T1.v10.mgz'  # for DKT atlas
        output_name = 'seg_hippo_rh_orig.mgz'
    else:
        input_name = 'mri/aseg.mgz'  # for Destrieux atlas
        output_name = 'seg_Destrieux_orig.mgz'

    input_path = os.path.join(freesurfer_subj, input_name)
    output_path = os.path.join(path_directory, steps[3], output_name)

    #ref file
    ref_name = 'mri/rawavg.mgz'
    ref_path = os.path.join(freesurfer_subj, ref_name)  # reslice to this file

    #Registration
    orig_space(input_path, ref_path, output_path)

    # Compute statistics on volume
    input_name = 'R1q_cor.nii.gz'
    input_path = os.path.join(path_directory, steps[1], input_name)
    seg_file_path = output_path                                               # files which contains the labels on the original space
    output_name = 'R1_per_regions_{}.txt'.format(atlas)
    output_path = os.path.join(path_directory, steps[3], output_name)


    stats_in_file(input_path, seg_file_path, output_path,freesurferHome)

    print("INFO : Print mean R1 regions values from {} atlas in R1_per_regions.txt".format(atlas))

def apply_processResults(path_directory, steps, freesurf_output_dir, subj_name, freesurferHome):
    """
    Apply brain mask on the R1 and T1 maps.
    Call the function to compute the R1 values in different ROIs

    Parameters
    ----------
    path_directory : string
        the path where all the pipeline results are stored, Should correspond to "processed_data_directory"
    steps : list of strings
      list containing the name of the steps performed on the pipeline
    freesurfer_output_dir : string
       path of the freesurfer subject directory
    subj_name : string
       subject folder name. Should looks like date_NIP.

    """
    mask_path = os.path.join(path_directory, steps[2], 'brain_mask.nii.gz')

    # Apply brain mask on T1
    input_path = os.path.join(path_directory, steps[1], 't1q_cor.nii.gz')
    output_path = os.path.join(path_directory, steps[3], 't1q_cor_brain.nii.gz')
    apply_mask(input_path, mask_path, output_path)

    del input_path, output_path

    # Apply brain mask on R1
    input_path = os.path.join(path_directory, steps[1], 'R1q_cor.nii.gz')
    output_path = os.path.join(path_directory, steps[3], 'R1q_cor_brain.nii.gz')
    apply_mask(input_path, mask_path, output_path)

    # Compute R1 values in differents region of the cotex and hippocampus
    freesurfer_subj = os.path.join(freesurf_output_dir, subj_name)
    atlas = ['hippo_lh', 'hippo_rh', 'dkt']
    for i in range(len(atlas)):
        R1_per_region(path_directory, steps, atlas[i], freesurfer_subj, freesurferHome)