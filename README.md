# MIE-2024
* Pending publication information and link
* Authors: 

## Purpose
MIE-2024 is a simple automation pipeline for bioinformatics guided synthesis of novel bioactive polyketide and non-ribosomal peptide natural products. Intended for use on the results of a protein BLAST , protein records homologous to enzymatic domain(s) of interest are used to identify nucleotide regions predicted to encode secondary metabolite products with desirable features. These regions are then extracted for annotation and secondary metabolite prediction, ultimately presenting these products as series of monomers suited for solid phase synthesis. The selectivity afforded by the initial screening primarily serves to reduce the computational load associated with metabolite prediction, with additional potential to guide cyclization and modification choices. 

## Required Third-Party Tools
The package relies on [antiSMASH](https://docs.antismash.secondarymetabolites.org/) for product prediction and [Biopython](https://biopython.org/) to interface with the NCBI Entrez API.

## Installation Components
- Python virtual environment for MIE-2024
- antiSMASH (7.1) local

## Installation Guide
Quick installation employs both conda and Git. For appropriate setup instructions for your device, please see their official documentation below.
> conda: <https://docs.conda.io/projects/conda/en/latest/> \
> Git: <https://git-scm.com/doc>

This installation configures MIE-2024 with its necessary dependencies, providing three user interactive scripts corresponding to the three major steps of the pipeline: ```do_filter```, ```do_prediction```, and ```do_synthesis```. These interactive scripts all include an optional welcome message, parameter explanations, and logging. The remaining script, ```user_end```, is not called directly but handles parameter checks, explanations, and directory management. 

### Python Virtual Environment
We recommend creating a conda environment with Python 3.12, using the following lines in a conda initialized terminal:

```Bash
conda create -n MIE-2024 python=3.12
conda activate MIE-2024
```

With this environment activated, all non-antiSMASH dependencies can be installed with the following command:
```Bash
pip install git+https://github.com/Parkinson-NP/MIE-2024
```

Environments are created and populated only once, then activated for later uses. If you have successfully activated your environment, your command prompt should begin with the environment name, ```(MIE-2024)```. A successfully populated environment will include *biopython*, *mie-2024*, and *numpy* in the environment packages displayed with ```conda list```. 

Problems with missing, incomplete, or duplicate environments can be resolved by viewing (```conda env list```) and deleting (```conda env remove -n environment_name```) environments. For more helpful commands, see the [official documentation from conda](https://docs.conda.io/projects/conda/en/stable/commands/index.html).

### antiSMASH Local
antiSMASH 7.1 can be run on most systems, however installation instructions will vary. Bioconda is used in this tutorial for a minimal setup. Alternative installation methods are detailed in the [official antiSMASH guide](https://docs.antismash.secondarymetabolites.org/#how-to-use-antismash-local-installation). Users with an existing installation of antiSMASH (version 7.0 or higher) do not need to reinstall.

To use Bioconda on a Windows computer, we recommend enabling [Windows Subsystem Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install) to establish a Linux terminal. Your terminal prompt should begin with your device name and newly established Linux username, for example ```USER@DEVICE:~$```. You will not have direct access to your Windows files and installations in this terminal, including conda.

In a Linux terminal as a non-root user, the following commands should be adequate to configure Bioconda and install antiSMASH in a new conda environment. 
```Bash
conda config --add channels bioconda
conda config --add channels conda-forge 
conda config --set channel_priority strict
```

```Bash
conda create --platform "linux-64" -n antiSMASH antismash
conda activate antiSMASH
download-antismash-databases
```

*antiSMASH* denotes the customizable environment name, while *antismash* indicates the necessary package to Bioconda. antiSMASH is not installed in the same environment as MIE-2024 to accommodate other antiSMASH integrations with possible dependency clashes.

# Use Instructions
## Filtering Protein Results
```do_filter``` utilizes Entrez to programmatically access NCBI protein records and retrieve the corresponding genome record, organized by CDS regions. User-supplied products of interest and other parameters are used to exclude records and regions not associated with desirable product features from further processing. Excluded records are not discarded, instead saved as JSON files for potential future analysis. In the event of failed record retrieval due to connectivity issues, an additional CSV of protein accessions is returned to be reran.

<img src="images/filter_overview.svg" width=400>

```do_filter``` can be called from any terminal with your ```MIE-2024``` conda environment activated.
```Bash
conda activate MIE-2024
python3 -m MIE_2024.do_filter
```

Your system may replace ```python3``` with ```python``` or ```py```. At the beginning of each run, you will be prompted to view an optional welcome message before continuing to enter mandatory and optional parameters. This message can also be used to confirm you are working in the intended terminal and environment.

For any input, you will have the opportunity to affirm and/or seek additional information about the parameter's requirements and usage. If at any point you supply an invalid input, you will be prompted again with additional detail. This information can also be called on demand by typing ```--help```. Similarly, ```--end``` can be used to terminate the program at any input or decision point.

## Secondary Metabolite Prediction
```do_prediction``` utilizes antiSMASH to predict and annotate nucleotide regions isolated by ```do_filter```. Primarily serving as a wrapper for normal command line activity with antiSMASH, ```do_prediction``` runs many records consecutively with the same parameters while checking for prediction success. If a nucleotide region is too small or has been improperly trimmed, antiSMASH is unable to provide metabolite prediction and the record accession will be returned in an additional CSV to be rerun.

<img src="images/prediction_overview.svg" width=400>

In contrast to ```do_filter``` and ```do_synthesis```, product prediction requires a Linux terminal with the antiSMASH environment activated. To access ```do_prediction``` from its installation in your initial environment, you will first need to identify and navigate to its directory.

```bash
conda activate antiSMASH
find /initial/path | grep "MIE_2024"
```
```bash
cd /full/path/returned/MIE_2024
```
For WSL users, this means searching your mounted drive, 
```/mnt/c```. Extending this initial path with more specificity, for example ```/mnt/c/users/username/anaconda3/envs``` can help reduce extraneous results.

With ```do_prediction``` now available in the antiSMASH environment, it can be invoked similarly to the other scripts. 
```bash
python3 do_prediction.py
```

```do_prediction``` relies only on the Python standard library, ensuring its dependencies are satisfied by those provided for antiSMASH. Other scripts may behave unexpectedly if run in the antiSMASH environment.

## Product Synthesis Guide
```do_synthesis``` is a short organizational script used to parse the collection of nested files produced by antiSMASH into a CSV. Results are indexed and organized as series of monomers, aligned with the sequential procedure of solid-phase peptide synthesis. For simplicity, only top monomer prediction abbreviations are included in the final sheet. Detailed prediction information can currently be found in the original antiSMASH JSON files and may be made available in CSV form in a later release.

<img src="images/synthesis_overview.svg" width=400>

```do_synthesis``` can be run identically to ```do_filter``` in the ```MIE-2024``` conda environment, where information is available through the initial welcome message and ```--help```.

```bash
conda activate MIE-2024
python3 -m MIE_2024.do_synthesis
```

# Support
Console information logged and saved in the subdirectory ```mie_2024_logs```, searchable by time of execution. Please utilize these logs in the event of unexpected program behavior to localize your issue to a particular script, dependency, or input case.

For related works and contact information, please visit [our website](https://www.parkinsonlaboratory.com/).

