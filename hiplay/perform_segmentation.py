import os
import subprocess as sub

def apply_segmentation(path_directory,steps,freesurf_output_dir, freesurferHome, subj_name):
    """
    Perform cortical and hippocampal parcellation based on T1w contrast image using Freesurfer recon-all [1][2]

    T1w image should correspond to the t1uni_den.nii.gz from the folder 1.Inputs of the path_directory

    Parameters
       ----------
       path_directory : string
           the path where all the pipeline results are stored, Should correspond to "processed_data_directory"
       steps : list of strings
           list containing the name of the steps performed on the pipeline
       freesurf_output_dir : string
            the path to the freesurfer subject directory to save all the freesurfer output
       freesurferHome : basestring
            the path directory where freesurfer has been stored
       subj_name : string
            the name of the subject folder. Should match the format Date_NIP

    Outputs
    ---------
    Compute the freesurfer outputs for each subject in the "freesurfer_output" folder. See freesurfer architecture for more information

     References
        ----------
    [1] Natalia Zaretskaya et al, Advantages of cortical surface reconstruction using submillimeter 7 T MEMPRAGE, 2018, NeuroImage 165
    [2] JE Iglesias, A computational atlas of the hippocampal formation using ex vivo, ultra-high resolutionMRI: Application to adaptive segmentation of in vivo MRI, Neuroimage, 2015

    """

    input_path = os.path.join(path_directory, steps[0], 't1uni_den.nii.gz')
    expert_file = os.path.join(freesurf_output_dir, 'expert.opts')
    output_dir=os.path.join(freesurf_output_dir,subj_name)

    # check inputs exist
    if not os.path.isfile(expert_file) :
        raise FileNotFoundError('Could not find {}. If the problem persists please copy it manually from the hiplay package'.format(expert_file))

    if not os.path.isfile(input_path) :
        raise FileNotFoundError('Could not find {}. Run again the whole process for the subject {}'.format(input_path,subj_name))

    # Initialise freesurfer variable environment
    ini_freesurfer = format("{}/SetUpFreeSurfer.sh".format(freesurferHome))

    # Perform cortical segmentation


    recon_all = format("{}/bin/recon-all -sd {} -s {} -i {} -hires -all -expert {}"
                       .format(freesurferHome, freesurf_output_dir, subj_name, input_path, expert_file))
    command1 = ini_freesurfer + ';' + recon_all
    try:
        print("INFO : Start cortical parcellation (~35h). Please wait")
        sub.check_call(command1, shell=True)
        print("INFO : End of cortical parcellation. Results stored in {}".format(output_dir))
    except sub.CalledProcessError:
        quit()


    # Perform Hippocampal segmentation

    seghip = format("{}/bin/recon-all -sd {} -s {} -hippocampal-subfields-T1 -cm".format(freesurferHome,freesurf_output_dir, subj_name))
    command2 = ini_freesurfer + ';' + seghip
    try:
        print("INFO : Start hippocampal parcellation (~1h). Please wait")
        sub.check_call(command2, shell=True)
        print("INFO : End of hippocampal parcellation. Results stored in {}".format(output_dir))
    except sub.CalledProcessError:
        quit()

