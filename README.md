# genelist-api

## Overview
This program will query KnetMiner based upon your user provided genes (must be seperated by a new line and contain ONLY your genes) and user provided keywords (same format as genes), which will return the knetscore, cromosome positions, and KnetMiner API links for all matching genes found in KnetMiner. This script thus so far only works for rice, wheat, and araboidopsis. 


## Prerequisites
* The script can run on any computer with Python3+. 

However, you may need to install the following, if not already installed:

* pandas
* numpy
* argparse
* requests

Simply perform a pip install, or use your environment manager to install these dependencies. 

* The program does not require heavy computational resources. However, as the user may prefer high performance computing the instructions on how to set up and run the program on a node managed by the Easybuild framework has been included below. The User should read set up instructions specific to any other HPC frameworks.

* Python virtual environments, e.g. virtualenv for python2 or pyvenv for python3. If the user does not have root permission on Easybuild a virtual environment is required for installation of requests, numpy and pandas through pip. See **4.Installing python request library** in **Instructions** on how to do this.

#### 1.Downloading the repository
Clone this repository with the GitHub URL using either Git or a Git GUI. The user should obtain a directory named gwas-gene-discovery containing identical contents to the GitHub repository.

#### 2. Accessing compute node on Easybuild
The user can check available compute nodes by the command:
```
sinfo 
```
If available, login to a standard compute node on Rothhpc4 using:
```
srun --pty bash -i
```

#### 3.Setting up a virtual environment on Easybuild
A virtual environment is required for pip installation of numpy, pandas, and requests.
Check all the available versions of python currently on cluster:
```
module avail Python
```
**Note that the virtualenv is only required if you lack permissions to install**
```
module load <Python3 version>
virtualenv <name of Python virtual environment>
source </path to env>/bin/activate/
```
The user can return to the virtual environment in a new session after logging out by:
```
module load <Python version>
source </path to env>/bin/activate/
```
  
#### 4.Execution of script
The command:
```
python genepage_insight.py -h
```
Returns the help page

The **mandatory arguments** are:
An example text file used for tutorial is example_list.txt. Example_list.txt contains a list of the first 5 wheat genes belonging to solstice and skyfall variety from [CerealsDB](http://www.cerealsdb.uk.net/cerealgenomics/CerealsDB/indexNEW.php) returned by a [prior investigation](https://github.com/colinliCitrolius/team3/blob/master/scores.tab).

There are four flags that can be provided, given as follows:

* ```-g``` OR ```--gene``` Corresponding to the name of the plain text file which contains your list of genes (you may need to provide the full directory if using the Python script elsewhere)
* ```-k``` OR ```--keywords``` Corresponding to the plaint text file which contains the description of phenotypes of interest to you, formatted by new lines. Again, you may need to provide the full directory.
* ```-s``` OR ```--species``` Corresponding to the 3 species options, from which you can choose ```rice```, ```wheat```, or ```arabidopsis``` (```ara```)
* ```-o``` OR ```-output``` This corresponds to your desired output directory, though it's non essential. If you don't provide this, a file will be created using your gene file name & appending ```_output``` to it, where your results & dependent files will be found.

```
python3 genepage-insight.py -g example_list.txt -k mock_keyword_list.txt -s wheat -o /home/$USER/test_output.txt
```

#### 5. Output information
The output will be a tabular text file containing 5 columns of Genes, Knetscore, chromosome, gene start position and network view.
To see an example of the result of the script, see ./example_list/results.txt

The Knetscore column assesses the relevance of the gene to the trait or traits of interest provided in the keyword list file. The higher the knetscore, the more likely the gene is to influence the trait.

The network view column contains URL addresses to networks of Knetminer which displays related orthologues, other traits encoded by the gene and publications etc. 


## External tools included
[Knetminer V3.0](https://knetminer.rothamsted.ac.uk/KnetMiner/)



## Authors
Keywan-Hassani Pak


Colin Li


Joseph Hearnshaw  



## Acknowledgement
Bioinformatics Department, [Computational and Analytical Sciences](https://www.rothamsted.ac.uk/computational-and-analytical-sciences), Rothamsted Resarch
