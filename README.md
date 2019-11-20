# genelist-api

## Overview
This script will query the KnetMiner Knowledge Graph with a user provided gene list (one gene id per line) and a user provided keyword file (one keyword per line). It returns the knetscore, genome location, and KnetMiner genepage URL for each user gene that can be associated with any of the keywords. The script was tested with upto 3000 wheat genes and 10 keywords. It currently only supports rice, wheat and araboidopsis. 


## Prerequisites
The script requires Python3+ with following dependecies:

* pandas
* numpy
* argparse
* requests

* Python virtual environments, e.g. pyvenv for python3. If the user does not have root permission on Easybuild a virtual environment is required for installation of the dependencies through pip. 

* The script uses the KnetMiner REST API and therefore requires an internet connection.

## Execution

### 1.Downloading the repository
Clone this repository with the GitHub URL using either Git or a Git GUI. The user should obtain a directory named gwas-gene-discovery containing identical contents to the GitHub repository.

### 2. Accessing compute node on Easybuild
The user can check available compute nodes by the command:
```
sinfo 
```
If available, login to a standard compute node on Rothhpc4 using:
```
srun --pty bash -i
```

### 3.Setting up a virtual environment on Easybuild
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
To install any of the required modules, please execute the following:

```pip install <module_name>``` 
  
### 4.Execution of script
The command:
```
python3 genepage_insight.py -h
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

### 5. Output information
The output will be a tabular text file containing 5 columns of Genes, Knetscore, chromosome, gene start position and network view.
To see an example of the result of the script, see ./example_list/results.txt

The Knetscore column assesses the relevance of the gene to the trait or traits of interest provided in the keyword list file. The higher the knetscore, the more likely the gene is to influence the trait.

The network view column contains URL addresses to networks of Knetminer which displays related orthologues, other traits encoded by the gene and publications etc. 


## Authors
[Keywan-Hassani Pak](https://github.com/KeywanHP)


[Colin Li](https://github.com/Haolin-Colin-Li)


[Joseph Hearnshaw](https://github.com/josephhearnshaw)
