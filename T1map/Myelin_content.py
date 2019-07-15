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

    # Create R1map
    output_name = 'R1q_cor.nii.gz'
    output_path = os.path.join(path_directory, steps[3], output_name)
    print('INFO : Create R1 map')
    # output, error = inv_image(input_path, output_path)
    print("INFO : R1 map created")

    del output_name, output_path, input_name, input_path

    # Apply brain mask on R1
    input_name = 'R1q_cor.nii.gz'
    input_path = os.path.join(path_directory, steps[3], input_name)
    output_name = 'R1q_cor_brain.nii.gz'
    output_path = os.path.join(path_directory, steps[3], output_name)
    apply_mask(input_path, mask_path, output_path)





def R1_per_tissu(path_directory, steps):
    # Create label tissu mask and save as nifti object
    print("INFO : Creation of tissus mask")
    file_name = 'T1_fast_seg.nii.gz'
    file_path = os.path.join(path_directory, steps[2], 'Tissus_seg.anat', file_name)
    tmp = nib.load(file_path)
    tissus = tmp.get_data()  # load datas from nifti image

    CSF = np.zeros(tissus.shape)
    # CSF[tissus == 1] = 1
    # path = os.path.join(path_directory, 'mask_CSF.nii.gz')
    # new_tmp = nib.Nifti1Image(CSF, tmp.affine, tmp.header)
    # new_tmp.to_filename(path)

    WM = np.zeros(tissus.shape)
    # WM[tissus == 3] = 1
    # path = os.path.join(path_directory, 'mask_WM.nii.gz')
    # new_tmp = nib.Nifti1Image(WM, tmp.affine, tmp.header)
    # new_tmp.to_filename(path)

    GM = np.zeros(tissus.shape)
    # GM[tissus == 2] = 1
    # path = os.path.join(path_directory, 'mask_GM.nii.gz')
    # new_tmp = nib.Nifti1Image(GM, tmp.affine, tmp.header)
    # new_tmp.to_filename(path)

    #Apply tissus mask on R1

    input_name = 'R1q_cor.nii.gz'
    input_path = os.path.join(path_directory, steps[3], input_name)
    tmp = nib.load(input_path)
    R1 = tmp.get_data()  # load datas from nifti image

    R1 = R1*1000

    R1_wm=R1[tissus==3]
    mean_wm =  R1_wm.mean()
    std_wm = np.std(R1_wm)

    R1_gm=R1[tissus==2]
    mean_gm = R1_gm.mean()
    std_gm = R1_gm.std()

    R1_csf = R1[tissus == 1]
    mean_csf = R1_csf.mean()
    std_csf = R1_csf.std()

    print("INFO : Print mean T1 tissus values in R1_per_tissus.txt")

    #write in a file
    file_output = 'R1_per_tissus.txt'
    path = os.path.join(path_directory, steps[3], file_output)
    F = open(path, 'w')
    F.write('R1 WM = {} +- {}\n'.format(mean_wm,std_wm))
    F.write('R1 GM = {} +- {}\n'.format(mean_gm,std_gm))
    F.write('R1 CSF = {} +- {}\n'.format(mean_csf,std_csf))

    F.close()


def R1_per_region(path_directory, steps,atlas):

    # Regis template to original space
    if atlas == 'dkt':
        input_name = 'mri/aparc.DKTatlas+aseg.mgz'         #for DKT atlas
        output_name = 'seg_DKT_orig.mgz'
    elif atlas == 'hippo':
        input_name = 'mri/lh.hippoSfLabels-T1.v10.mgz'  # for DKT atlas
        output_name = 'seg_hippo_orig.mgz'
    else:
        input_name = 'mri/aseg.mgz'  # for Destrieux atlas
        output_name = 'seg_Destrieux_orig.mgz'

    input_path = os.path.join(path_directory, steps[2], 'Region_seg', input_name)
    file_name = 'mri/rawavg.mgz'
    file_path= os.path.join(path_directory, steps[2], 'Region_seg', file_name)     # reslice to this file
    output_path = os.path.join(path_directory, steps[3], output_name)

    orig_space(input_path, file_path, output_path)


    # Compute statistics on volume
    input_name = 't1q_cor.nii.gz'
    input_path = os.path.join(path_directory, steps[1], input_name)
    seg_file_path = output_path                                               # files which contains the labels on the original space
    output_name = 'T1_per_regions.txt'
    output_path = os.path.join(path_directory, steps[3], output_name)

    freesurferHome = '/neurospin/grip/protocols/MRI/HIPLAY7_mr_2019/Prog/freesurfer'

    stats_in_file(input_path, seg_file_path, output_path, freesurferHome)

    print("INFO : Print mean T1 regions values from {} atlas in T1_per_regions.txt".format(atlas))