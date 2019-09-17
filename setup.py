
import setuptools

pkgdata = {
    "hiplay": ["expert.opts", "MR_system_parameters"],
}

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hiplay",
    version="1.1.0",
    author="Mathilde Ripart",
    author_email="mathilde.ripart@example.com",
    description="Map the myelin content in brain for the HIPLAY7 project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mathrip/HIPLAY7",
    packages=setuptools.find_packages(),
    package_data=pkgdata,
    scripts=["hiplay/scripts/myelin_content"],
    install_requires=[
        "matplotlib",
        "numpy",
        "scipy",
        "nibabel",
        "dicom2nifti"],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",    
	],
)
