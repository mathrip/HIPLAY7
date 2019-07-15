import os
import nibabel as nib
import numpy as np
import math
from scipy import signal
import re

def apply_mask(path_input, mask, path_output):
    from subprocess import Popen, PIPE
    fslmaths = ["fslmaths",
                "{}".format(path_input),
                "-mul", "{}".format(mask),
                "{}".format(path_output)]
    fslmaths_cmd = Popen(fslmaths, stdout=PIPE)
    fslmaths_output, fslmaths_error = fslmaths_cmd.communicate()
    return fslmaths_output, fslmaths_error

def inv_image(path_input, path_output):
    from subprocess import Popen, PIPE
    fslmaths = ["fslmaths",
                "{}".format(path_input),
                "-recip",
                "{}".format(path_output)]
    fslmaths_cmd = Popen(fslmaths, stdout=PIPE)
    fslmaths_output, fslmaths_error = fslmaths_cmd.communicate()
    return fslmaths_output, fslmaths_error

def orig_space(path_input, path_file, path_output):
    from subprocess import Popen, PIPE
    mriconvert = ["mri_convert",
                  "-rt", "nearest",
                  "-rl", "{}".format(path_file),
                  "{}".format(path_input),
                  "{}".format(path_output)]
    mriconvert_cmd = Popen(mriconvert, stdout=PIPE)
    mriconvert_output, mriconvert_error = mriconvert_cmd.communicate()
    return mriconvert_output, mriconvert_error

def stats_in_file(path_input, labels3D, path_output, freesurferHome):
    from subprocess import Popen, PIPE
    labels = os.path.join(freesurferHome,'FreeSurferColorLUT.txt')
    mrisegstats = ["mri_segstats",
                  "--seg", "{}".format(labels3D),
                  "--sum", "{}".format(path_output),
                  "--i","{}".format(path_input),
                  "--ctab","{}".format(labels)]
    mrisegstats_cmd = Popen(mrisegstats, stdout=PIPE)
    mrisegstats_output, mrisegstats_error = mrisegstats_cmd.communicate()
    return mrisegstats_output, mrisegstats_error


def process_results(path_directory, steps):
    mask_name = 'T1_biascorr_brain_mask.nii.gz'
    mask_path = os.path.join(path_directory, steps[2], 'Tissus_seg.anat', mask_name)

    # Apply brain mask on T1
    input_name = 't1q_cor.nii.gz'
    input_path = os.path.join(path_directory, steps[1], input_name)
    output_name = 't1q_cor_brain.nii.gz'
    output_path = os.path.join(path_directory, steps[3], output_name)
    apply_mask(input_path, mask_path, output_path)

    del output_name, output_path

    # Apply brain mask on R1
    input_name = 'R1q_cor.nii.gz'
    input_path = os.path.join(path_directory, steps[3], input_name)
    output_name = 'R1q_cor_brain.nii.gz'
    output_path = os.path.join(path_directory, steps[3], output_name)
    apply_mask(input_path, mask_path, output_path)


def R1_per_region(path_directory, steps, atlas, freesurfer_subj):

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
    #orig_space(input_path, ref_path, output_path)

    # Compute statistics on volume
    input_name = 'R1q_cor.nii.gz'
    input_path = os.path.join(path_directory, steps[1], input_name)
    seg_file_path = output_path                                               # files which contains the labels on the original space
    output_name = 'R1_per_regions_{}.txt'.format(atlas)
    output_path = os.path.join(path_directory, steps[3], output_name)

    freesurferHome = '/neurospin/grip/protocols/MRI/HIPLAY7_mr_2019/Prog/freesurfer'
    stats_in_file(input_path, seg_file_path, output_path, freesurferHome)

    print("INFO : Print mean R1 regions values from {} atlas in R1_per_regions.txt".format(atlas))