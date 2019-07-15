import os
import shutil
import subprocess

def segmentation_tissus(input_path, output_dir):
    # segmentation on CSF, WM and GM using the fsl_anat pipeline
    # input :T1w contrast
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
    # subprocess.call('bet {} {} -f {}'.format(path_input,path_output,fraction),shell=True)
    from subprocess import Popen, PIPE
    bet = ["bet",
           "{}".format(path_input),
           "{}".format(path_output),
           "-m",
           "-f", "{}".format(fraction),]
    bet_cmd = Popen(bet, stdout=PIPE)
    bet_output, bet_error = bet_cmd.communicate()
    return bet_output, bet_error

def cortical_parcellation(input_file, subj_name, freesurf_output_dir, expert_file):
    # segmentation on CSF, WM and GM using the freesurfer recon-all pipeline
    # input :T1w contrast
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

def segmentation_Hippo(name, subjects_dir):
    # segmentation on CSF, WM and GM using the freesurfer recon-all pipeline
    # input :T1w contrast
    from subprocess import Popen, PIPE
    seghip = ["recon-all",
                   "-sd", "{}".format(subjects_dir),
                   "-s", "{}".format(name),
                   "-hippocampal-subfields-T1",
                   "-cm"]
    seghip_cmd = Popen(seghip, stdout=PIPE)
    seghip_output, seghip_error = seghip_cmd.communicate()
    return seghip_output, seghip_error

def apply_pipeline_seg(path_directory,steps,freesurf_output_dir,subj_name):

    input_file= 't1uni_den.nii.gz'
    input_path = os.path.join(path_directory, steps[0],input_file)
    output_dir_name = 'brain'
    output_dir= os.path.join(path_directory,steps[2],output_dir_name)
    output, error = brain_extraction(input_path, output_dir, 0.3)

    # Perform cortical segmentation and parcellation
    expert_file = os.path.join(freesurf_output_dir, 'expert.opts')
    #
    print("INFO : Start cortical parcellation")
    output, error = cortical_parcellation(input_path,subj_name,freesurf_output_dir, expert_file)
    print("INFO : End of cortical parcellation")
    #
    # Perform Hippocampal segmentation
    #
    # subjects_dir = os.path.join(path_directory, steps[2])
    #
    print("INFO : Start hippocampal segmentation")
    output, error = segmentation_Hippo(subj_name, freesurf_output_dir)
    print("INFO : End of hippocampa segmentation")


