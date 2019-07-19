import os

def skullstripped(input_path, output_dir):
    from subprocess import Popen, PIPE
    fslanat = ["fsl5.0-fsl_anat",
                "-i", "{}".format(input_path),
                "-o", "{}".format(output_dir),
                "--nocrop",
                "--nosubcortseg"]
    fslanat_cmd = Popen(fslanat, stdout=PIPE)
    fslanat_output, fslanat_error = fslanat_cmd.communicate()
    return fslanat_output, fslanat_error

def brain_extraction(path_input, path_output, fraction):
    """ perform brain extraction with the function bet from FSL

    Parameters
       ----------
       path_input : string
           the path to the image to do the brain extraction
       path_output : string
           the path to save the new image brain extracted
       fraction : fractional intensity threshold
    """
    from subprocess import Popen, PIPE
    bet = ["bet",
           "{}".format(path_input),
           "{}".format(path_output),
           "-m",
           "-f", "{}".format(fraction)]
    bet_cmd = Popen(bet, stdout=PIPE)
    bet_output, bet_error = bet_cmd.communicate()
    return bet_output, bet_error

def cortical_parcellation(input_file, subj_name, freesurf_output_dir, expert_file):
    """ perform cortical parcellation with the function recon-all from FreeSurfer based on T1w contrast

        Parameters
           ----------
           input_file : string
               the name of the T1 contrast image to use for the cortical parcellation
           subj_name : string
                the name of the subject folder. Should match the format Date_NIP
           freesurf_output_dir : string
                the path to the freesurfer subject directory to save all the freesurfer output
           expert_file : string
                the path to the file expert.opt where the option for high resolution parcellation are stored [1]

        References
            ----------
         [1] Natalia Zaretskaya et al, Advantages of cortical surface reconstruction using submillimeter 7 T MEMPRAGE, 2018, NeuroImage 165
    """
    from subprocess import Popen, PIPE
    recon_all = ["recon-all",
                   "-sd", "{}".format(freesurf_output_dir),
                   "-s", "{}".format(subj_name),
                   "-i", "{}".format(input_file),
                   "-hires",
                   "-all",
                   "-expert", "{}".format(expert_file)]
    reconall_cmd = Popen(recon_all, stdout=PIPE)
    reconall_output, reconall_error = reconall_cmd.communicate()
    return reconall_output, reconall_error

def segmentation_Hippo(subj_name, freesurf_output_dir):
    """ perform hippocampus parcellation with the function recon-all from FreeSurfer based on T1w contrast
        Need to precise the flag -hippocampal-subfields-T1 [1]

           Parameters
              ----------
              subj_name : string
                   the name of the subject folder. Should match the format Date_NIP
              freesurf_output_dir : string
                   the path to the freesurfer subject directory to save all the freesurfer output

           References
               ----------
            [1] JE Iglesias, A computational atlas of the hippocampal formation using ex vivo, ultra-high resolutionMRI: Application to adaptive segmentation of in vivo MRI, Neuroimage, 2015
    """
    from subprocess import Popen, PIPE
    seghip = ["recon-all",
                   "-sd", "{}".format(freesurf_output_dir),
                   "-s", "{}".format(subj_name),
                   "-hippocampal-subfields-T1",
                   "-cm"]
    seghip_cmd = Popen(seghip, stdout=PIPE)
    seghip_output, seghip_error = seghip_cmd.communicate()
    return seghip_output, seghip_error

def apply_segmentation(path_directory,steps,freesurf_output_dir,subj_name):
    """ Perform brain extraction, cortical and hippocampal parcellation based on T1w contrast image

        T1w image should correspond to the t1uni_den.nii.gz from the folder 1.Inputs of the path_directory

        Parameters
           ----------
           path_directory : string
               the path where all the pipeline results are stored, Should correspond to "processed_data_directory"
           steps : list of strings
               list containing the name of the steps performed on the pipeline
           subj_name : string
                the name of the subject folder. Should match the format Date_NIP
           freesurf_output_dir : string
                the path to the freesurfer subject directory to save all the freesurfer output

    """

    #Brain extraction
    input_path = os.path.join(path_directory, steps[0],'t1uni_den.nii.gz')
    output_dir= os.path.join(path_directory,steps[2],'brain')
    print("INFO : Start skull-stripping")
    output, error = skullstripped(input_path, output_dir)
    print("INFO : End of skull stripping. Results stored in {}".format(output_dir))

    # Perform cortical segmentation and parcellation
    expert_file = os.path.join(freesurf_output_dir, 'expert.opts')
    print("INFO : Start cortical parcellation")
    output, error = cortical_parcellation(input_path,subj_name,freesurf_output_dir, expert_file)
    print("INFO : End of cortical parcellation. Results stored in {}".format(freesurf_output_dir))

    # Perform Hippocampal segmentation
    print("INFO : Start hippocampal parcellation")
    output, error = segmentation_Hippo(subj_name, freesurf_output_dir)
    print("INFO : End of hippocampa parcellation. Results stored in {}".format(freesurf_output_dir))


