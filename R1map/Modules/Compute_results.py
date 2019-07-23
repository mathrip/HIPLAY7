import os

def apply_mask(path_input, mask, path_output):
    """
    Apply binary mask to an image using the function mris_calc from Freesurfer

    Parameters
    ----------
        path_input : string
            path of the image (in .nii or .nii.gz) to apply the mask on
        mask : string
            path to the binary mask in .mgz
        path_output : string
            the path of the folder on which to save the output on
    """
    from subprocess import Popen, PIPE
    mrisCalc = ["mris_calc",
                "-o","{}".format(path_output),
                "{}".format(path_input),
                "masked", "{}".format(mask)]
    mrisCalc_cmd = Popen(mrisCalc, stdout=PIPE)
    mrisCalc_output, mrisCalc_error = mrisCalc_cmd.communicate()
    return mrisCalc_output, mrisCalc_error

def orig_space(path_input, path_ref, path_output):
    """
    Coregister the a freesurfer output volume to the original space of the subject using
    the function mriconvert from FreeSurfer

    Parameters
    ----------
        path_input : string
            path of the image (.mgz) to apply registration
        path_ref : string
            path to the freesurfer recon-all output "mri/rawavg.mgz" to use as a reference
        path_output : string
            path to save the new volume (.mgz)
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
            path of the image that contains the labels of the atlas in the subject original space (.mgz)
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


def apply_processResults(path_directory, steps, freesurf_output_dir, subj_name, freesurferHome):
    """
    Skull-stripped and remove CSF from R1 and T1 maps.
    Register the ROI in the original space of the T1 map
    Compute the R1 values in different ROIs

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
    freesurferHome : string
        path of the freesurfer installation folder

    """
    freesurfer_subj = os.path.join(freesurf_output_dir, subj_name)


    # Register mask to original space
    ref_name = 'mri/rawavg.mgz'                                                     # file for registration to original space
    ref_path = os.path.join(freesurfer_subj, ref_name)
    mask_path = os.path.join(freesurfer_subj, 'mri/ribbon.mgz')                         # mask of gm+wm (remove CSF and skull)
    mask_new_path = os.path.join(path_directory, steps[2], 'brainmask_orig.mgz')
    orig_space(mask_path, ref_path, mask_new_path)                                  # Registration

    # Apply brain mask on T1 and R1
    input_path = os.path.join(path_directory, steps[1], 't1q_cor.nii.gz')
    output_path = os.path.join(path_directory, steps[3], 't1q_cor_clean.nii.gz')
    apply_mask(input_path, mask_new_path, output_path)

    del input_path, output_path

    # Apply brain mask on R1
    input_path = os.path.join(path_directory, steps[1], 'R1q_cor.nii.gz')
    output_path = os.path.join(path_directory, steps[3], 'R1q_cor_clean.nii.gz')
    apply_mask(input_path, mask_new_path, output_path)

    # Compute R1 values in differents region of the cotex and hippocampus
    atlas = ['hippo_lh', 'hippo_rh', 'dkt']                                         # anytging else would perform the destrieux atlas
    for i in range(len(atlas)):
        if atlas[i] == 'dkt':
            print('INFO : Compute statistics in DKT atlas')
            input_name = 'mri/aparc.DKTatlas+aseg.mgz'                              # for DKT atlas
            output_name = 'seg_DKT_orig.mgz'
        elif atlas[i] == 'hippo_lh':
            print('INFO : Compute statistics in left hippocampus atlas')
            input_name = 'mri/lh.hippoSfLabels-T1.v10.mgz'                          # for left hippocampus atlas
            output_name = 'seg_hippo_lh_orig.mgz'
        elif atlas[i] == 'hippo_rh':
            print('INFO : Compute statistics in right hippocampus atlas')
            input_name = 'mri/rh.hippoSfLabels-T1.v10.mgz'                          # for right hippocampus atlas
            output_name = 'seg_hippo_rh_orig.mgz'
        else:
            print('INFO : Compute statistics in Destrieux atlas')
            input_name = 'mri/aseg.mgz'  # for Destrieux atlas                      # for Destrieux atlas
            output_name = 'seg_Destrieux_orig.mgz'

        input_path = os.path.join(freesurfer_subj, input_name)
        output_path = os.path.join(path_directory, steps[2], output_name)

        # Register atlas labels to original space
        orig_space(input_path, ref_path, output_path)

        # Compute statistics on volume
        input_name = 'R1q_cor.nii.gz'
        input_path = os.path.join(path_directory, steps[1], input_name)
        seg_file_path = output_path                                                  # files which contains the labels on the original space
        output_name = 'R1_per_regions_{}.txt'.format(atlas[i])
        output_path = os.path.join(path_directory, steps[3], output_name)

        stats_in_file(input_path, seg_file_path, output_path, freesurferHome)

        print("INFO : Print mean R1 regions values from {} atlas in {}".format(atlas[i],output_name))