import os

def apply_segmentation(path_directory,steps,freesurf_output_dir,subj_name):
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
       subj_name : string
            the name of the subject folder. Should match the format Date_NIP

     References
        ----------
    [1] Natalia Zaretskaya et al, Advantages of cortical surface reconstruction using submillimeter 7 T MEMPRAGE, 2018, NeuroImage 165
    [2] JE Iglesias, A computational atlas of the hippocampal formation using ex vivo, ultra-high resolutionMRI: Application to adaptive segmentation of in vivo MRI, Neuroimage, 2015

    """
    from subprocess import Popen, PIPE
    input_path = os.path.join(path_directory, steps[0], 't1uni_den.nii.gz')
    expert_file = os.path.join(freesurf_output_dir, 'expert.opts')
    output_dir=os.path.join(freesurf_output_dir,subj_name)

    print("INFO : Start cortical parcellation (~35h)")
    recon_all = ["recon-all",
                   "-sd", "{}".format(freesurf_output_dir),
                   "-s", "{}".format(subj_name),
                   "-i", "{}".format(input_path),
                   "-hires",
                   "-all",
                   "-expert", "{}".format(expert_file)]
    recon_all_cmd = Popen(recon_all, stdout=PIPE)
    recon_all_output, recon_all_error = recon_all_cmd.communicate()
    print("INFO : End of cortical parcellation. Results stored in {}".format(output_dir))

    # Perform Hippocampal segmentation
    print("INFO : Start hippocampal parcellation (~1h)")
    seghip = ["recon-all",
              "-sd", "{}".format(freesurf_output_dir),
              "-s", "{}".format(subj_name),
              "-hippocampal-subfields-T1",
              "-cm"]
    Popen(seghip, stdout=PIPE)
    seghip_cmd = Popen(seghip, stdout=PIPE)
    seghip_output, seghip_error = seghip_cmd.communicate()
    print("INFO : End of hippocampal parcellation. Results stored in {}".format(output_dir))
