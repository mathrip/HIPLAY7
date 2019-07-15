
import numpy as np
import nibabel as nib
import os
# Create label tissu mask and save as nifti object

path_directory = '/neurospin/grip/protocols/MRI/HIPLAY7_mr_2019/Python_Carto_T1/pipelineV1'

file_name = 'T1_fast_seg.nii.gz'
file_path = os.path.join(path_directory, 'Tissus_seg.anat', file_name)
tmp = nib.load(file_path)
tissus = tmp.get_data()  # load datas from nifti image

#CSF = np.zeros(tissus.shape)
# CSF[tissus == 1] = 1
# path = os.path.join(path_directory, 'mask_CSF.nii.gz')
# new_tmp = nib.Nifti1Image(CSF, tmp.affine, tmp.header)
# new_tmp.to_filename(path)

#WM = np.zeros(tissus.shape)
# WM[tissus == 3] = 1
# path = os.path.join(path_directory, 'mask_WM.nii.gz')
# new_tmp = nib.Nifti1Image(WM, tmp.affine, tmp.header)
# new_tmp.to_filename(path)

#GM = np.zeros(tissus.shape)
# GM[tissus == 2] = 1
# path = os.path.join(path_directory, 'mask_GM.nii.gz')
# new_tmp = nib.Nifti1Image(GM, tmp.affine, tmp.header)
# new_tmp.to_filename(path)

# Apply tissus mask on qT1
input_name = 't1q.nii.gz'
input_path = os.path.join(path_directory, input_name)
tmp = nib.load(input_path)
qT1 = tmp.get_data()  # load datas from nifti image

input_name = 't1q_cor.nii.gz'
input_path = os.path.join(path_directory, input_name)
tmp = nib.load(input_path)
qT1_cor = tmp.get_data()  # load datas from nifti image


qT1_wm = qT1[tissus == 3]
mean_wm = qT1_wm.mean()
std_wm = np.std(qT1_wm)

qT1_gm = qT1[tissus == 2]
mean_gm = qT1_gm.mean()
std_gm = qT1_gm.std()

qT1_csf = qT1[tissus == 1]
mean_csf = qT1_csf.mean()
std_csf = qT1_csf.std()

qT1_cor_wm = qT1_cor[tissus == 3]
mean_wm_cor = qT1_cor_wm.mean()
std_wm_cor = np.std(qT1_cor_wm)

qT1_cor_gm = qT1_cor[tissus == 2]
mean_gm_cor = qT1_cor_gm.mean()
std_gm_cor = qT1_cor_gm.std()

qT1_cor_csf = qT1_cor[tissus == 1]
mean_csf_cor = qT1_cor_csf.mean()
std_csf_cor = qT1_cor_csf.std()

print("INFO : Print mean T1 tissus values in T1values.txt")

# write in a file
file = 'T1values.txt'
path = os.path.join(path_directory, file)
F = open(path, 'w')
F.write('qT1 WM = {} +- {}\n'.format(mean_wm, std_wm))
F.write('qT1 GM = {} +- {}\n'.format(mean_gm, std_gm))
F.write('qT1 CSF = {} +- {}\n'.format(mean_csf, std_csf))
F.write('qT1_cor WM = {} +- {}\n'.format(mean_wm_cor, std_wm_cor))
F.write('qT1_cor GM = {} +- {}\n'.format(mean_gm_cor, std_gm_cor))
F.write('qT1_cor CSF = {} +- {}\n'.format(mean_csf_cor, std_csf_cor))
F.write('diff WM = {} \n'.format(mean_wm_cor-mean_wm))
F.write('diff WM = {} \n'.format(mean_wm_cor-mean_wm))
F.write('diff WM = {} \n'.format(mean_wm_cor-mean_wm))

F.close()

# see histogramm
import matplotlib.pyplot as plt
import scipy.stats as stats



density_wm = stats.gaussian_kde(qT1_wm)
count,bins_wm= np.histogram(qT1_wm, 500, normed=True)  # arguments are passed to np.histogram
plt.plot(bins_wm, density_wm(bins_wm),linewidth=2, color='g')

density_gm = stats.gaussian_kde(qT1_gm)
count,bins_gm= np.histogram(qT1_gm, 500, normed=True)  # arguments are passed to np.histogram
plt.plot(bins_gm,density_gm(bins_gm),linewidth=2, color='r')

density_wm_cor = stats.gaussian_kde(qT1_cor_wm)
count,bins_wm_cor= np.histogram(qT1_cor_wm, 500, normed=True)  # arguments are passed to np.histogram
plt.plot(bins_wm_cor, density_wm_cor(bins_wm_cor),linewidth=2, color='b')

density_gm_cor = stats.gaussian_kde(qT1_cor_gm)
count,bins_gm_cor= np.histogram(qT1_cor_gm, 500, normed=True)  # arguments are passed to np.histogram
plt.plot(bins_gm_cor,density_gm_cor(bins_gm_cor),linewidth=2, color='k')

plt.xlim((0,3000))
plt.xlabel('T1 (ms)')
plt.ylabel('Probability')
plt.title(r'Histogram of T1 values before and after correction')
legend = ['T1 WM','T1 GM','T1 WM corrected ','T1 GM corrected']
plt.legend(legend)
plt.show()

plt.hist(qT1_gm, bins=500, facecolor='skyblue', histtype='step', normed=1)  # arguments are passed to np.histogram
plt.hist(qT1_cor_wm, bins=1000, facecolor='pink',histtype='step', normed=1)  # arguments are passed to np.histogram
plt.hist(qT1_cor_gm, bins=1000, facecolor='red',histtype='step', normed=1)  # arguments are passed to np.histogram
legend = ['T1 WM','T1 GM','T1 WM corrected ','T1 GM corrected']


plt.show()
