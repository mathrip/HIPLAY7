
import matplotlib.pyplot as plt
import os
import nibabel as nib
import numpy as np

subject_directory ='/neurospin/grip/protocols/MRI/HIPLAY7_mr_2019/Pipeline_results/20190605_ek190023'

# View image gray scale with color bar

path_t1 = os.path.join(subject_directory, '4.qMyelin/t1q_brain.nii.gz')
tmp=nib.load(path_t1)
t1c = tmp.get_data()    #load datas from nifti image
t1c = np.rot90(t1c)

plt.subplot(221)
plt.imshow(t1c[:,:,160], cmap='gray')
plt.title('T1(ms)')
plt.subplot(222)
plt.imshow(t1c[:,:,160], cmap='gray')
cax = plt.axes([0.1, 0.1, 0.075, 0.8])
plt.colorbar(orientation='horizontal', pad=0.2)
plt.clim(0,4000)
plt.axis('off')
plt.show()



# Display T1q et T1q_cor
import matplotlib.gridspec as gridspec
files=['4.qMyelin/t1q_brain.nii.gz','4.qMyelin/t1q_cor_brain.nii.gz']
title=['T1q', 'T1q corrected']
gs1 = gridspec.GridSpec(1, 2)
fig, axs = plt.subplots(1, 2, constrained_layout=True)
ind=0
for ax in axs.flat:
    #open file
    path = os.path.join(subject_directory, files[ind])
    tmp = nib.load(path)
    t1c = tmp.get_data()  # load datas from nifti image
    #rotate matrix for good display
    t1c = np.rot90(t1c)
    #display image
    im = ax.imshow(t1c[:,:,160], cmap='gray')
    ax.set_title(title[ind])
    ax.set_xticklabels('')
    ax.set_yticklabels('')
    ax.set_aspect('equal')
    ind=ind+1
#set the color bar
cbar = fig.colorbar(im, ax=ax, shrink=0.6, pad=0, orientation="vertical")
cbar.set_label('T1 (ms) ', rotation=270)
fig.set_constrained_layout_pads(w_pad=2./72., h_pad=2./72.,
        hspace=0, wspace=0)
gs1.tight_layout(fig)

# Display diff t1q -t1q_cor map
files=['4.qMyelin/t1q_brain.nii.gz','4.qMyelin/T1q_cor_brain.nii.gz']
path_1 = os.path.join(subject_directory, files[0])
tmp = nib.load(path_1)
t1q = tmp.get_data()  # load datas from nifti image
path_2 = os.path.join(subject_directory, files[1])
tmp = nib.load(path_2)
t1q_c = tmp.get_data()  # load datas from nifti image

diff_t1q = t1q.astype(float)-t1q_c.astype(float)
diff_t1q = np.rot90(diff_t1q)

plt.imshow(diff_t1q[:,:,160], cmap='RdBu')
plt.title('Difference')
# cax = plt.axes([10, 50, 100, 120])
cbar = plt.colorbar(orientation='vertical', pad=0.2)
cbar.set_label('T1 (ms) ', rotation=270)
plt.clim(-60,60)
plt.axis('off')
plt.show()


# Display R1 map
path_t1 = os.path.join(subject_directory, '4.qMyelin/R1q_cor_brain.nii.gz')
tmp=nib.load(path_t1)
t1c = tmp.get_data()    #load datas from nifti image
t1c = np.rot90(t1c)

t1c = t1c*1000
plt.imshow(t1c[:,:,160], cmap='gray')
plt.title('R1 map')
# cax = plt.axes([10, 50, 100, 120])
cbar = plt.colorbar(orientation='vertical', pad=0.2)
cbar.set_label('R1 (s) ', rotation=270)
plt.clim(0,1)
plt.axis('off')
plt.show()


# Display B1 map in percentage
path_b1 = os.path.join(subject_directory, '2.B0_correction/b1_to_mp2r.nii.gz')
tmp=nib.load(path_b1)
b1 = tmp.get_data()    #load datas from nifti image
# b1 = np.rot90(b1)

b1 = b1/6
plt.imshow(b1[:,:,160], cmap='winter')
plt.title('FA (% target)')
# cax = plt.axes([10, 50, 100, 120])
plt.colorbar(orientation='vertical', pad=0.2)
plt.clim(20,100)
plt.axis('off')
plt.show()

# Display B1 mask > threshold
mask_conf = np.zeros(b1.shape)
mask_conf[b1>=70] = 1

path = os.path.join(subject_directory, '2.B0_correction/B0_mask.nii.gz')
new_tmp = nib.Nifti1Image(mask_conf, tmp.affine, tmp.header)
new_tmp.to_filename(path)

plt.imshow(mask_conf[:,:,160], cmap='gray')
plt.axis('off')
plt.show()

path_t1 = os.path.join(subject_directory, '4.qMyelin/t1q_brain.nii.gz')
tmp=nib.load(path_t1)
t1c = tmp.get_data()    #load datas from nifti image
t1c = np.rot90(t1c)

t1c_mask=t1c*mask_conf
plt.imshow(t1c_mask[:,:,160], cmap='gray')
plt.axis('off')
plt.show()