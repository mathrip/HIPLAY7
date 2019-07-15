import matplotlib.pyplot as plt
import os
import re
import numpy as np
import pandas as pd
import matplotlib.pylab as plt

subject_directory ='/neurospin/grip/protocols/MRI/HIPLAY7_mr_2019/Pipeline_test/20190605_ek190023'

path_T1 = os.path.join(subject_directory,'4.qMyelin')


# display stats on destrieux atlas
files = os.path.join(path, 'T1_per_regions.txt')
roi_name = ["" for x in range(44)]
mean_int = ["" for x in range(44)]
stdDev_int = ["" for x in range(44)]
words = []
with open(files, encoding='latin-1') as f:  # return reference value from dicom data
    inc = 0
    for line in f:
            li = line.strip()
            if not li.startswith("#"):
                words = line.split()
                roi_name[inc] = words[4]
                mean_int[inc] = float(words[5])
                stdDev_int[inc] = float(words[6])
                print('In {} the T1 value is {} +- {}'.format(roi_name[inc],mean_int[inc],stdDev_int[inc]))
                inc = inc + 1

plt.errorbar(range(len(roi_name)), mean_int, stdDev_int, linestyle='None',uplims=True, lolims=True, fmt='o')
plt.xticks(range(len(roi_name)), roi_name, rotation='vertical')
plt.subplots_adjust(bottom=0.5)
plt.ylabel('T1 (s)')
plt.title(r'Average T1 and standard deviation in different roi of the brain')

plt.show()

# display stats on dkt ATLAS
path = '/neurospin/grip/protocols/MRI/HIPLAY7_mr_2019/Python_Carto_T1/test_seg_freesurfer/analyse_stat'
files = os.path.join(path, 'resultsDKT.aseg.sum')

roi_name = ["" for x in range(64)]
roi_full_name = ["" for x in range(64)]
mean_int = ["" for x in range(64)]
stdDev_int = ["" for x in range(64)]
words = []
with open(files, encoding='latin-1') as f:  # return reference value from dicom data
    inc = 0
    for line in f:
            li = line.strip()
            if not li.startswith("#"):
                words = line.split()
                indice = float(words[0])
                if indice>= 45:
                    roi_full_name[inc] = words[4]
                    roi_name[inc] = roi_full_name[inc].split('-')[2]
                    mean_int[inc] = float(words[5])
                    stdDev_int[inc] = float(words[6])
                    print('In {} the T1 value is {} +- {}'.format(roi_name[inc],mean_int[inc],stdDev_int[inc]))
                    inc = inc + 1

plt.errorbar(range(len(roi_name)), mean_int, stdDev_int, linestyle='None',uplims=True, lolims=True, fmt='o',color='r')
plt.xticks(range(len(roi_name)), roi_name, rotation='vertical')
plt.subplots_adjust(bottom=0.5)
plt.ylabel('T1 (ms)')
plt.title(r'Average T1 and standard deviation in the DKT atlas')

plt.show()


# Other test : comparison with qT1 before correction

files =["" for x in range(2)]
files[0] = os.path.join('/neurospin/grip/protocols/MRI/HIPLAY7_mr_2019/Python_Carto_T1/test_seg_freesurfer/analyse_stat/t1q.aseg.sum')
files[1] = os.path.join('/neurospin/grip/protocols/MRI/HIPLAY7_mr_2019/Python_Carto_T1/test_seg_freesurfer/analyse_stat/t1q_cor.aseg.sum')
color=['b','k']
i=0
for i in range(2):
    roi_name = ["" for x in range(44)]
    mean_int = ["" for x in range(44)]
    stdDev_int = ["" for x in range(44)]
    words = []
    with open(files[i], encoding='latin-1') as f:  # return reference value from dicom data
        inc = 0
        for line in f:
                li = line.strip()
                if not li.startswith("#"):
                    words = line.split()
                    roi_name[inc] = words[4]
                    mean_int[inc] = float(words[5])
                    stdDev_int[inc] = float(words[6])
                    print('In {} the T1 value is {} +- {}'.format(roi_name[inc],mean_int[inc],stdDev_int[inc]))
                    inc = inc + 1
    plt.errorbar(range(len(roi_name)), mean_int, stdDev_int, linestyle='None', uplims=True, lolims=True, fmt='o', color=color[i])
    i=i+1
plt.xticks(range(len(roi_name)), roi_name, rotation='vertical')
plt.subplots_adjust(bottom=0.5)
plt.ylabel('T1 (s)')
labels=['Original data', 'With B1 correction']
plt.legend(labels)
plt.title(r'Average T1 and standard deviation in different roi of the brain')
plt.show()


# Other test : comparison between 2 subjects

subject_directory1 ='/neurospin/grip/protocols/MRI/HIPLAY7_mr_2019/Pipeline/20190605_ek190023'
path1 = os.path.join(subject_directory1,'4.qMyelin')

subject_directory2 ='/neurospin/grip/protocols/MRI/HIPLAY7_mr_2019/Pipeline/20190619_md130174'
path2 = os.path.join(subject_directory2,'4.qMyelin')

files =["" for x in range(2)]
files[0] = os.path.join(path1, 'T1_per_regions.txt')
files[1] = os.path.join(path2, 'T1_per_regions.txt')
color=['b','r']
marker = ['--', '--']
i=0
for i in range(2):
    roi_name = ["" for x in range(44)]
    mean_int = ["" for x in range(44)]
    stdDev_int = ["" for x in range(44)]
    words = []
    with open(files[i], encoding='latin-1') as f:  # return reference value from dicom data
        inc = 0
        for line in f:
                li = line.strip()
                if not li.startswith("#"):
                    words = line.split()
                    roi_name[inc] = words[4]
                    mean_int[inc] = float(words[5])
                    stdDev_int[inc] = float(words[6])
                    print('In {} the T1 value is {} +- {}'.format(roi_name[inc],mean_int[inc],stdDev_int[inc]))
                    inc = inc + 1
    plt.errorbar(range(len(roi_name)), mean_int, stdDev_int, linestyle='None', uplims=True, lolims=True, fmt='o', color=color[i])
    i=i+1
plt.xticks(range(len(roi_name)), roi_name, rotation='vertical')
plt.subplots_adjust(bottom=0.5)
plt.ylabel('T1 (s)')
labels=['CSF corrected data', 'CSF non corrected']
plt.legend(labels)
plt.title(r'Average T1 and standard deviation in different roi of the brain')
plt.show()