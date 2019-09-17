import os
import subprocess as sub

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


    Outputs
    ---------
    Compute the following output in the folder "3.Segmentation" of the subject directory :
            brainmask_orig.mgz : freesurfer mask of the brain in the original space
            seg_DKT_orig.mgz : freesurfer cortical parcellation in the original space based on Desikan-Kiliany atlas
            seg_hippo_lh_orig.mgz : freesurfer left hippocampal parcellation in the original space
            seg_hippo_rh_orig.mgz : freesurfer right hippocampal parcellation in the original space

     Compute the following output in the folder "4.Results" of the subject directory :
            R1q_cor_clean.nii.gz: Final R1 map skull-stripped
            T1q_cor_clean.nii.gz: Final T1 map skull-stripped
            R1_per_regions_dkt.txt : text file with the average R1 values on the cortical ROIs
            R1_per_regions_hippo_lh.txt : text file with the average R1 values on the left hippocampal ROIs
            R1_per_regions_hippo_rh.txt : text file with the average R1 values on the right hippocampal ROIs

    """
    
    freesurfer_subj = os.path.join(freesurf_output_dir, subj_name)
    
    print('INFO : Compute R1 values in different ROIs')

    # Register mask to original space
    ref_name = 'mri/rawavg.mgz'                                                            # file for registration to original space
    ref_path = os.path.join(freesurfer_subj, ref_name)
    mask_path = os.path.join(freesurfer_subj, 'mri/brainmask.mgz')                         # mask of gm+wm (remove CSF and skull)
    mask_new_path = os.path.join(path_directory, steps[2], 'brainmask_orig.mgz')

    mrisconvert = format("{}/bin/mri_convert -rt nearest -rl {} {} {}"
                         .format(freesurferHome, ref_path, mask_path, mask_new_path ))
    try:
        sub.check_call(mrisconvert, shell=True)
    except sub.CalledProcessError:
        pass


    ## Apply brain mask on T1 and R1
    input_path = os.path.join(path_directory, steps[1], 't1q_cor.nii.gz')
    output_path = os.path.join(path_directory, steps[3], 't1q_cor_clean.nii.gz')

    mrisCalc = format("{}/bin/mris_calc -o {} {} masked"
                      .format(freesurferHome, output_path, input_path, mask_new_path))
    try:
        sub.check_call(mrisCalc, shell=True)
    except sub.CalledProcessError:
        pass


    del input_path, output_path


    ## Apply brain mask on R1
    input_path = os.path.join(path_directory, steps[1], 'R1q_cor.nii.gz')
    output_path = os.path.join(path_directory, steps[3], 'R1q_cor_clean.nii.gz')

    mrisCalc = format("{}/bin/mris_calc -o {} {} masked"
                      .format(freesurferHome, output_path, input_path, mask_new_path))
    try:
        sub.check_call(mrisCalc, shell=True)
    except sub.CalledProcessError:
        pass

    ## Compute R1 values in differents region of the cotex and hippocampus
    atlas = ['hippo_lh', 'hippo_rh', 'dkt']                                                 # anytging else would perform the destrieux atlas
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
        mrisconvert = format("{}/bin/mri_convert -rt nearest -rl {} {} {}"
                             .format(freesurferHome, ref_path, input_path, output_path))
        try:
            sub.check_call(mrisconvert, shell=True)
        except sub.CalledProcessError:
            pass


        # Compute statistics on volume
        input_name = 'R1q_cor.nii.gz'
        input_path = os.path.join(path_directory, steps[1], input_name)
        seg_file_path = output_path                                                  # files which contains the labels on the original space
        output_name = 'R1_per_regions_{}.txt'.format(atlas[i])
        output_path = os.path.join(path_directory, steps[3], output_name)

        color_labels = os.path.join(freesurferHome, 'FreeSurferColorLUT.txt')
        mrisegstats = format("{}/bin/mri_segstats --seg {} --sum {} --i {} --ctab {}"
                             .format(freesurferHome, seg_file_path, output_path, input_path, color_labels))

        try:
            sub.check_call(mrisegstats, shell=True)
            print("INFO : Print mean R1 regions values from {} atlas in {}".format(atlas[i], output_name))
        except sub.CalledProcessError:
            pass


