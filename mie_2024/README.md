# Project Title
## Headline

* some info about the piece, ex. accompanying paper and authors
* beta version for the Parkinson Lab

## Purpose
Effectively comb blast-p results at bgc level before committing to product prediction; then automate product prediction and translation to synthesis sheet

## Required Third-Party Tools
The package relies on antiSMASH (<https://docs.antismash.secondarymetabolites.org/>) for product prediction and Biopython (<https://biopython.org/>) to interface with the NCBI Entrez API.

## Installation Components
- Python virtual environment
- Unix compatible operating system or environment
- antiSMASH local

## Installation Guide
Quick installation employs both Conda and Git. If you have not worked with these tools before, their documentation is linked below.
> Conda: <https://docs.conda.io/projects/conda/en/latest/>
>
> Git: <https://git-scm.com/doc>

### Python Virtual Environment
We reccomend creating a Conda environment with Python 3.12, using the following lines in a Conda initialized terminal:
```Bash
conda create -n MIE-2024 python=3.12
conda activate MIE-2024
```
With this environment activated, all non-antiSMASH dependencies can be installed with the following command:
```Bash
pip install git+https://github.com/Parkinson-NP/MIE-2024
```

### Unix Compatible OS or Environment
AntiSMASH 7.1 does not offer support for the Windows OS. There are many options available to configure a Unix compatible environment on Windows OS. Native Unix users may proceed to installation of antiSMASH local.

 As an example, setup of Windows Subsystem Linux (WSL) with Ubuntu is used here. For additional WSL tips and FAQs, official instructions are available at <https://learn.microsoft.com/en-us/windows/wsl/install>.

[//]: # (Depending on your software version, you may need to enable WSL before moving forwards.
WSL can be enabled via Administrator commands in Windows Powershell, or graphically in Windows Control Panel.)  
[//]: # (*Virtual Machine Platform* and *Windows Subsystem for Linux* must be enabled under **Windows Control Panel > Programs > Programs and Features > Turn Windows features on or off**. With the required features enabled, installation can be then be carried out graphically in the Microsoft Store, or with the following command in Windows Powershell:)
[//]: # (Bash
wsl --install -d Ubuntu)  


If choosing to install your distribution from the Microsoft Store, please ensure you have set up a Linux user account before proceeding. Your terminal prompt should show your device name and newly established Unix username like so:
 ```Bash
 USER@DEVICE:~$ 
 ```
This terminal prompt indicates you are sucessfully operating in a Unix environment, where you will not have direct access to  your Windows files or installations. To continue with Quick Installation, you'll need to configure Anaconda or Miniconda for your new Unix environment. Miniconda will provide the necessary packages for the least storage space, and can be installed as instructed in *Quick command line install* for Linux: <https://docs.anaconda.com/miniconda/>.

## AntiSMASH Local
In a Unix terminal as a non-root user, the following commands will be adequate to configure Bioconda and install antiSMASH local in a new Conda environment. *antiSMASH* denotes the environment name (customizable), while *antismash* indicates the necessary package to Bioconda. antiSMASH is not installed in the same environment as MIE-2024 in anticipation of other antiSMASH integrations with possible dependency clashes.
```Bash
conda config --add channels bioconda
conda config --add channels conda-forge 
conda config --set channel_priority strict
conda create -n antiSMASH antismash
conda activate antismash
download-antismash-databases
conda deactivate
```
Bioconda is one of 3 supported installation methods from antiSMASH. Instructions for Docker or manual installation can be found at <https://docs.antismash.secondarymetabolites.org/install/>.
# Use Instructions
## Programs 1 and 3
Programs 1 and 3 are OS independent - these can be called from any terminal with your Conda environment activated.
```bash
python3 do_program1.py
python3 do_program2.py
```
Once initiated, you will be prompted to view an optional welcome message before continuing to enter mandatory and optional parameters. This message can also be used to confirm you are working in the intended environment.

For any user input, you will have the opportunity to affirm your choice and/or seek additional information about the parameter's requirements and usage. If at any point you supply an invalid input, you will be reprompted with additional detail. This information can also be called from the dictionary ```user_input.explanations``` on demand.

## Program 2
Program 2 utilizes antiSMASH, and must be run from a Unix terminal in the antiSMASH environment. To run program 2 as it exists in your initial environment, you will first need to identify the neccessary path and navigate to it. 
For WSL users, this means searching your mounted drive, 
```/mnt/c/users/username```. Extending this initial path with more specificity, for example ```/mnt/c/users/username/anaconda3/envs``` can help cut down on extraneous results.

```bash
conda activate antiSMASH
find /initial/path | grep "mie_2024/programs"
cd /full/path/returned/mie_2024/programs
```
With program 2 now available in the antiSMASH environment, it can be called like programs 1 and 3. 
```bash
python3 do_program2.py
```
To avoid risking dependency clashes between these and any antiSMASH integration programs, please refrain from running programs 1 and 3 in the antiSMASH environment.

\
<img src="p1_11112024.svg" width=400>

<img src="p3_11112024.svg" width=400>
