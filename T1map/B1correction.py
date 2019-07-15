#Module
import os
import nibabel as nib
import numpy as np
import math
from scipy import signal as sig
import re
import matplotlib.tri as tri
import shutil

from functions_old import resampling

def inv_image(path_input, path_output):
    from subprocess import Popen, PIPE
    fslmaths = ["fslmaths",
                "{}".format(path_input),
                "-recip",
                "-mul 1000",
                "{}".format(path_output)]
    fslmaths_cmd = Popen(fslmaths, stdout=PIPE)
    fslmaths_output, fslmaths_error = fslmaths_cmd.communicate()
    return fslmaths_output, fslmaths_error

def correct_from_B1(path_directory, steps) :
#Correct the T1_image and T1_uni of the MP2RAGE sequence from the B1+ inhomogeneities
# INPUT in the path directory :
# t1q.nii.gz : T1 image from the MP2RAGE sequence
# t1uni.nii.gz : T1 uni image from the MP2RAGE sequence
# b1map.nii.gz : b1 map obtain from the xfl sequence
# info_b1, info_t1_image : one dicom image from b1 and t1_image dicoms folder

#OUTPUT in the path_directory :
# b1_to_mp2r.nii.gz : b1map resampled at the T1 mp2rage resolution
# t1q_cor.nii : T1 map corrected from the B1+
# t1uni_cor.nii : T1 uni corrected from the B1+

    #---------- 1 Process the B1map--------------####
    # 1.1 Apply median filter on B1map to remove noise

    file_name = 'b1map.nii.gz'
    path = os.path.join(path_directory, steps[0], file_name)
    tmp=nib.load(path)
    b1 = tmp.get_data()    #load datas from nifti image

    b1 = b1.astype(float)   # convert in float
    k=0
    while k < tmp.shape[2] :
        b1[:,:,k] = sig.medfilt2d(b1[:,:,k])
        k = k + 1
    np.uint16(b1)
    file_name2 ='b1_to_mp2r.nii.gz'
    path = os.path.join(path_directory, steps[1], file_name2)
    new_tmp = nib.Nifti1Image(b1, tmp.affine, tmp.header)
    new_tmp.to_filename(path)

    del tmp, new_tmp , b1, path, file_name, file_name2


    #1.2 Resample B1map to T1map
    path_in = os.path.join(path_directory,steps[1], 'b1_to_mp2r.nii.gz')
    path_ref = os.path.join(path_directory,steps[0], 't1uni.nii.gz')
    path_out = os.path.join(path_directory,steps[1], 'b1_to_mp2r.nii.gz')

    resampling(path_in,path_ref,path_out)

    del path_in, path_out, path_ref

    #1.3 Apply offset FAnom outside B1+ FOV

    file_name = 'b1_to_mp2r.nii.gz'
    path = os.path.join(path_directory, steps[1], file_name)
    tmp= nib.load(path)
    b1 = tmp.get_data()

    flipAngle = 60
    b1[b1==0] = flipAngle*10

    #1.4 correction for reference value

    dicom_name = ['info_b1','info_t1_image']
    ref_value=[0,0]
    for i in range(2):
        files = os.path.join(path_directory,steps[0],dicom_name[i])

        with open(files, encoding='latin-1') as f:  #return reference value from dicom data
            for line in f:
                line = line.strip()
                if re.match(r'(.*)flReferenceAmplitude(.*)',line):
                    line_split = re.split(r'=',line)
                    ref_value[i] = int(line_split[1])

    ref_b1 = ref_value[0]
    ref_mp2r = ref_value[1]
    coef_ref = ref_mp2r/ref_b1
    b1 = b1 * coef_ref

    path = os.path.join(path_directory, steps[1], file_name)
    new_tmp = nib.Nifti1Image(b1, tmp.affine, tmp.header)
    new_tmp.to_filename(path)

    del tmp, new_tmp , b1, path, file_name


#-----------2 Add B1+ correction to T1map-----------------

    #2.1 Load T1 uni

    file_name = 't1uni.nii.gz'
    path = os.path.join(path_directory,steps[0],file_name)
    tmp= nib.load(path)
    uni = tmp.get_data()
    uni = uni/4096-0.5


    #2.2 Load b1 map and create a relative map

    file_name = 'b1_to_mp2r.nii.gz'
    path = os.path.join(path_directory,steps[1],file_name)
    tmp= nib.load(path)
    B1m = tmp.get_data()

    flipAngleNom = flipAngle*10*coef_ref
    B1map_rel = 100/flipAngleNom*B1m
    B1map_rel[B1map_rel<20]  = 20                   # limit B1 from 20% to 120% nominal value for corection
    B1map_rel[B1map_rel>120] = 120
    B1 = [i for i in range(20,121)]                 # go from 200% B1 to 120% B1
    B1 = np.int32(B1)

    #2.3 Calculate theoretical MP2RAGE signal for a given B1rel and T1 range

    # Update MP2RAGE parameters here (this should be the protocol run on the MR system)
    file = '/home/mr259480/PycharmProjects/HIPLAY7/T1map/MR_system_parameters'
    newfile = os.path.join(path_directory,steps[1],'MR_system_parameters')
    shutil.copyfile(file,newfile)
    param_system = [0 for i in range(9)]
    with open(newfile, encoding='latin-1') as f:  # return reference value from dicom data
        i = 0
        for line in f:
            line = line.strip()
            line_split = re.split(r'=', line)
            param_system[i] = float(line_split[1])
            i = i+1

    T1 = np.arange(200, 5000, 10)         # list of T1 in ms
    alpha1deg = param_system[0]  # FA1 in deg
    alpha2deg = param_system[1]  # FA2 in deg
    nbefore = param_system[2]  # FLASH pulses before k-space center
    nafter = param_system[3]  # FLASH pulses after k-space center
    n = nbefore + nafter  # Total number of FLASH pulses = number of slices * PF(slice)
    TR = param_system[4]  # Echo spacing in ms
    BTR = param_system[5]  # Sequence TR in ms
    TI1 = param_system[6]  # First inversion time in ms
    TI2 = param_system[7]  # Second inversion time in ms
    eff = param_system[8]  # Inversion efficiency for adiabatic pulse (empirical)

    # Intermediate terms
    TA = TI1 - nbefore * TR  # TA with PF
    TB = TI2 - TI1 - n * TR  # TB with PF
    TC = BTR - TI2 - nafter * TR  # TC with PF
    E1 = np.exp(-(np.divide(TR, T1)))
    EA = np.exp(-(np.divide(TA, T1)))
    EB = np.exp(-(np.divide(TB, T1)))
    EC = np.exp(-(np.divide(TC, T1)))
    M0 = 1  # Magnetization
    C = 1

    k = 0
    signal = np.zeros((T1.shape[0], B1.shape[0]))
    matrix = np.zeros((T1.shape[0], B1.shape[0]))
    while k < B1.shape[0]:  # loop over different B1rel values
        B1rel = (B1[k].astype(float)) / 100
        alpha1cor = alpha1deg / 180 * math.pi * B1rel  # corrected FA1 in rad
        alpha2cor = alpha2deg / 180 * math.pi * B1rel  # corrected FA2 in rad
        SA1 = math.sin(alpha1cor)
        SA2 = math.sin(alpha2cor)
        CA1 = math.cos(alpha1cor)
        CA2 = math.cos(alpha2cor)

        # Steady state FLASH signal PFourier ok
        tmp1 = np.divide((1 - (CA1 * E1) ** n), (1 - (CA1 * E1)))  # PFourier ok
        tmp2 = np.divide((1 - (CA2 * E1) ** n), (1 - (CA2 * E1)))  # PFourier ok
        num = M0 * ((((1 - EA) * (CA1 * E1) ** n + (1 - E1) * tmp1) * EB + (1 - EB)) * (CA2 * E1) ** n + (
                1 - E1) * tmp2) * EC + (1 - EC);  # PFourier ok
        den = 1 + eff * (CA1 * CA2) ** n * np.exp(-(np.divide(BTR, T1)))  # PFourier ok
        mzss = np.divide(num, den)

        # Signal in the middle of the First readout --> only nbefore matters
        MZtemp = ((-eff * mzss * np.divide(EA, M0) + (1 - EA)) * (CA1 * E1) ** (nbefore) + (1 - E1) * np.divide(
            (1 - (CA1 * E1) ** (nbefore)), (1 - (CA1 * E1))))
        GRETI1 = C * SA1 * MZtemp

        # Signal in the middle of the First readout --> both nbefore and nafter matter
        MZtemp = MZtemp * (CA1 * E1) ** (nafter) + (1 - E1) * np.divide((1 - (CA1 * E1) ** (nafter)),
                                                                        (1 - (CA1 * E1)))  # PFourier ok
        MZtemp = (MZtemp * EB + (1 - EB)) * (CA2 * E1) ** (nbefore) + (1 - E1) * np.divide(
            (1 - (CA2 * E1) ** (nbefore)), (1 - CA2 * E1))  # PFourier ok
        GRETI2 = C * SA2 * MZtemp

        # Resulting signal (a.u. or dicom levels)
        SMP2R = np.divide((GRETI1 * GRETI2), (GRETI1 ** 2 + GRETI2 ** 2))

        signal[:, k] = SMP2R

        # little trick for correct CSF
        value = -0.5
        near_value = SMP2R.flat[np.abs(SMP2R - value).argmin()]
        ind = np.where(SMP2R == near_value)
        # vect = np.zeros((1, len(SMP2R)))
        vect = SMP2R
        vect[np.int(ind[0]):vect.shape[0]] = near_value

        signal[:,k] = vect


        # matrix[:, k] = vect
        k = k + 1

    # 2.4 create abaque and interpolation

    #Generate 2D T1 and B1 object matching signal's size
    T12D = np.tile(T1,(B1.shape[0],1)).T

    B12D = np.tile(B1,(T1.shape[0],1))
    B12D = B12D.astype(float)

    #Generate 2D interpolant

    triang = tri.Triangulation(B12D.flatten(),signal.flatten())
    interpolator = tri.LinearTriInterpolator(triang, T12D.flatten())

    # 2.5 Compute T1 unbiased and saved it as Nifti object
    zi = interpolator(B1map_rel, uni)

    # Calculate corrected T1 data on the measured B1/signal grid
    T1map=zi
    T1map[np.isnan(T1map)]=4096


    # Save Nifti
    file_name = 't1q.nii.gz'
    path = os.path.join(path_directory, steps[0],file_name)
    tmp= nib.load(path)

    file_name= 't1q_cor.nii.gz'
    path = os.path.join(path_directory, steps[1], file_name)
    new_tmp = nib.Nifti1Image(T1map, tmp.affine, tmp.header)
    new_tmp.to_filename(path)

    del tmp, new_tmp , path, file_name

    print("INFO : End of T1q correction")

    # ----------------3 compute R1 corrected ---------------------------------------------------------#

    input_name = 't1q_cor.nii.gz'
    input_path = os.path.join(path_directory, steps[1], input_name)
    output_name = 'R1q_cor.nii.gz'
    output_path = os.path.join(path_directory, steps[1], output_name)
    print('INFO : Create R1 map')
    output, error = inv_image(input_path, output_path)
    print("INFO : R1 map created")


    #----------------4 Recreate SYN UNI volume for 'std MP2R' protocol with B1+ correction and denoising---------------------------------------------------------#

    # 3.1 Load T1 uni original

    file_name = 't1q_cor.nii.gz'
    path = os.path.join(path_directory,steps[1],file_name)
    tmp= nib.load(path)
    T1map_cor = tmp.get_data()
    T1map_cor = T1map_cor.astype(float)

    # 3.2 Compute a synthetic T1uni unbiased from the T1q unbiased

    #Recreate UNI MP2R protocol

    alpha1deg = param_system[0]  # FA1 in deg
    alpha2deg = param_system[1]  # FA2 in deg
    nbefore = param_system[2]  # FLASH pulses before k-space center
    nafter = param_system[3]  # FLASH pulses after k-space center
    n = nbefore + nafter  # Total number of FLASH pulses = number of slices * PF(slice)
    TR = param_system[4]  # Echo spacing in ms
    BTR = param_system[5]  # Sequence TR in ms
    TI1 = param_system[6]  # First inversion time in ms
    TI2 = param_system[7]  # Second inversion time in ms
    eff = param_system[8]  # Inversion efficiency for adiabatic pulse (empirical)

# Intermediate terms
    TA = TI1-nbefore*TR        # TA with PF
    TB = TI2-TI1-n*TR          # TB with PF
    TC = BTR-TI2-nafter*TR     # TC with PF
    E1 = np.exp(-(np.divide(TR,T1map_cor)))
    EA = np.exp(-(np.divide(TA,T1map_cor)))
    EB = np.exp(-(np.divide(TB,T1map_cor)))
    EC = np.exp(-(np.divide(TC,T1map_cor)))
    M0 = 1                     # Magnetization
    C = 1
    SA1=math.sin(alpha1deg/180*math.pi)
    SA2=math.sin(alpha2deg/180*math.pi)
    CA1=math.cos(alpha1deg/180*math.pi)
    CA2=math.cos(alpha2deg/180*math.pi)


    # Steady state FLASH signal   PFourier ok
    # Steady state FLASH signal PFourier ok
    tmp1 = np.divide((1 - (CA1 * E1) ** n), (1 - (CA1 * E1)))  # PFourier ok
    tmp2 = np.divide((1 - (CA2 * E1) ** n), (1 - (CA2 * E1)))  # PFourier ok
    num = M0 * ((((1 - EA) * (CA1 * E1) ** n + (1 - E1) * tmp1) * EB + (1 - EB)) * (CA2 * E1) ** n + (1 - E1) * tmp2) * EC + (1 - EC);  # PFourier ok
    den = 1 + eff * (CA1 * CA2) ** n * np.exp(-(np.divide(BTR, T1map_cor)))  # PFourier ok
    mzss = np.divide(num, den)


    #Signal in the middle of the First readout --> only nbefore matters
    MZtemp=((-eff*mzss*np.divide(EA,M0)+(1-EA))*(CA1*E1)**(nbefore)+(1-E1)*np.divide((1-(CA1*E1)**(nbefore)),(1-(CA1*E1))))
    GRETI1=C*SA1*MZtemp

    # Signal in the middle of the First readout --> both nbefore and nafter matter
    MZtemp = MZtemp* (CA1*E1)**(nafter) + (1-E1)* np.divide((1- (CA1*E1)**(nafter)),(1 - (CA1 * E1))) # PFourier ok
    MZtemp = (MZtemp* EB + (1-EB))*(CA2* E1)**(nbefore) + (1-E1)*np.divide((1 - (CA2* E1)**(nbefore)),(1 - CA2* E1)) # PFourier ok
    GRETI2 = C * SA2 * MZtemp

    #Resulting signal (a.u. or dicom levels)
    SMP2R=np.divide((GRETI1*GRETI2),(GRETI1**2+GRETI2**2))

    # Going back to DICOM levels
    SMP2R_dicom=np.int16(SMP2R*4096+2048)


    # 3.3 Save synthetic T1 uni corrected as Nifti object

    #Export data
    file_name = 't1uni.nii.gz'
    path = os.path.join(path_directory,steps[0],file_name)
    tmp= nib.load(path)

    file_name= 't1uni_cor.nii.gz'
    path = os.path.join(path_directory,steps[1], file_name)
    new_tmp = nib.Nifti1Image(SMP2R_dicom, tmp.affine, tmp.header)
    new_tmp.to_filename(path)

    print("INFO : End of T1uni correction")
