# genelist-api

## Overview
The instructions below provide users with a copy of this program which can be directly used or adapted for their own project. The program require 2 plain text files, one containing a list of geneIDs and the other with a list of keywords describing the phenotypes the user suspects the genes have influence over. The script can work for either rice, wheat or arabidopsis.

The tabular output would provide the users with the chromosome and start position for every gene, a knetscore which assesses the relevance of each gene to the specified phenotype or phenotypes and a Knetminer genepage url per gene.
The url leads the user into Knetminer's network view which accelerates research by outlining orthology of the gene as well as traits and publications related to it.

## Prerequisites
* The script can run on any computer with Python3+. 

However, you will need to install the following, if not already installed:

*__future__
* pandas
* numpy
* argparse
* json
* requests
* itertools

Simply perform a pip install, or use your environment manager to install these dependencies. 

* The program does not require heavy computational resources. However, as the user may prefer high performance computing the instructions on how to set up and run the program on a node managed by the Easybuild framework has been included below. The User should read set up instructions specific to any other HPC frameworks.

* Python virtual environments, e.g. virtualenv for python2 or pyvenv for python3. If the user does not have root permission on Easybuild a virtual environment is required for installation of requests, numpy and pandas through pip. See **4.Installing python request library** in **Instructions** on how to do this.


## Tutorial and usage instructions
This is a quick tutorial to get the user started by reproducing the outputs of map_snp_to_gene.py for 2 different GWAS result spreadsheets, GAPIT.MLM.DTF.GWAS.Results.csv and GAPIT.MLM.blupWidth.GWAS.Results.csv as seen in the 2 directories of the same names. The tutorial generally assumes the user is using linux managed by Easybuild.

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
A virtual environment is required for pip installation of numpy, pandas and requests.
Check all the available versions of python currently on cluster:
```
module avail Python
```
After the user has decided on a version of Python2 that is 2.7 and above or Python3 execute the commands below.

```
module load <Python version>
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
python genepage-insight.py -g example_list.txt -k mock_keyword_list.txt -s wheat -o /home/$USER/test_output.txt
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
