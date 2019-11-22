# KnetMiner genome and genepage API
This script will query the KnetMiner Knowledge Graph with a user provided gene list (one gene ID per line) and a user provided keyword file (one keyword per line). It returns the knetscore, genome location, and KnetMiner genepage URL for each user gene that can be associated with any of the keywords. The script was tested with upto 3000 wheat genes and 10 keywords. It currently only supports rice, wheat and araboidopsis. 

## Prerequisites
The script requires Python3+ with following dependecies:

* pandas
* numpy
* argparse
* requests

* Python virtual environments, e.g. pyvenv for python3. If the user does not have root permission on Easybuild a virtual environment is required for installation of the dependencies through pip. 

* The script uses the KnetMiner REST API and therefore requires an internet connection.

## Execution

### Downloading the repository
Clone or download this repository using the green "Clone or Download" button. To clone this repository via git (command-line), simple execute the following:

``` git clone https://github.com/Rothamsted/genelist-api.git``` 

You'll find all the relevant files in the genelist-api folder, cloned to whatever directory you cloned it in. 

### Setting up Python and dependencies
Login to a compute node:
```
srun --pty bash -i
```

Check available versions of python:
```
module avail Python
module load <Python3 version>
```

A virtualenv is required if you lack permissions to pip install
```
virtualenv <name of Python virtual environment>
source </path to env>/bin/activate/
```

Install missing python packages:
```
pip install pandas
pip install numpy
pip install argparse
pip install requests
``` 
  
### Run the script
Change to the cloned/downloaded script folder. To see the script help page run:
```
python3 genepage_insight.py -h
```
Supported arguments are:
* ```-g``` OR ```--gene``` Text file which contains your list of gene ids or names (one per line)
* ```-k``` OR ```--keywords``` Text file which contains the search terms or keywords of interest to you (one er line). 
* ```-s``` OR ```--species``` Currently spporting ```rice```, ```wheat```, or ```arabidopsis``` (```ara```)
* ```-o``` OR ```-output``` Output directory. If npt provided, a file will be created using your gene file name & appending '_output' to it, where your results & dependent files will be found.

Example command:
```
python3 genepage-insight.py -g example_list.txt -k keywords_heat.txt -s wheat -o /home/$USER/test_output.txt
```

## Output information
The output will be a tabular text file containing 5 columns: Gene ID, Knetscore, Chromosome, Gene start and Network URL.

The Knetscore indicates the relevance of a gene to the provided keywords as described in Hassani-Pak (2017), PhD thesis.

The URL links to an interactive knowledge network of that gene with links to publications, ontologies, pathways etc that contain the keywords. 


## Authors
[Keywan-Hassani Pak](https://github.com/KeywanHP)


[Colin Li](https://github.com/Haolin-Colin-Li)


[Joseph Hearnshaw](https://github.com/josephhearnshaw)
