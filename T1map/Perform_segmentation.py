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


def cortical_parcellation(input_file, output_dir, name, expert_file,subject_dir):
    # segmentation on CSF, WM and GM using the freesurfer recon-all pipeline
    # input :T1w contrast
    from subprocess import Popen, PIPE
    recon_all = ["export SUBJECTS_dir=","{}".format(subject_dir),
                   "recon-all",
                   "-sd", "{}".format(output_dir),
                   "-s", "{}".format(name),
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

def apply_pipeline_seg(path_directory,steps):

    input_name= 't1uni_den.nii.gz'
    input_path = os.path.join(path_directory, steps[0],input_name)
    output_dir_name = 'Tissus_seg'
    output_dir= os.path.join(path_directory,steps[2],output_dir_name)

    # Perform segmentation tissus
    print("INFO : Start tissus segmentation")
    output, error = segmentation_tissus(input_path,output_dir)
    print("INFO : End of tissus segmentation")

    # Perform cortical segmentation and parcellation

    file = '/home/mr259480/PycharmProjects/HIPLAY7/T1map/expert.opts'
    expert_file = os.path.join(path_directory, steps[2], 'expert.opts')
    shutil.copyfile(file, expert_file)

    output_dir_name = 'Region_seg'
    output_dir = os.path.join(path_directory, steps[2])

    print("INFO : Start cortical parcellation")
    from subprocess import Popen, PIPE
    command=['source /neurospin/grip/protocols/MRI/HIPLAY7_mr_2019/Prog/freesurfer/SetUpFreeSurfer.sh']   #set up environment freesurfer
    executeCommand = Popen(command, stdout=PIPE)
    output, error = cortical_parcellation(input_path, output_dir, output_dir_name, expert_file,subject_dir)
    print("INFO : End of cortical parcellation")

    # Perform Hippocampal segmentation

    name_dir = 'Region_seg'
    subjects_dir = os.path.join(path_directory, steps[2])

    print("INFO : Start hippocampal segmentation")
    output, error = segmentation_Hippo(name_dir, subjects_dir)
    print("INFO : End of hippocampa segmentation")

