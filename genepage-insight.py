#!/usr/bin/python
from __future__ import print_function
import os
import math
import datetime
import requests
import json
import argparse
import shutil
import sys
import pandas as pd
import numpy as np
import resource
from itertools import islice
import pprint


def mkfolder():
    '''Create a folder for each gapit results, copy result.csv and reference into that directory.
    All results will then be generated within it. The main function will take the script back into parent.'''
    print("Commenced at {}".format(datetime.datetime.now()))
    folder=str(args.genes)[:-4] + "_output"
    if os.path.exists(folder):
        shutil.rmtree(folder)
        os.mkdir(folder)
        shutil.copy(args.genes, folder)
        shutil.copy(args.keywords, folder)
        os.chdir(folder)
    else:
        os.mkdir(folder)
        shutil.copy(args.genes, folder)
        shutil.copy(args.keywords, folder)
        os.chdir(folder)

def decode(r):
    """ If the request fails, then exit. Else, return the KnetMiner genetable.
        REQUIRES: The request.
        RETURNS: JSON object containing the gene-table information.
    """
    if not r.ok:
            r.raise_for_status()
            sys.exit()
    else:
        print("request successful")

    decoded=r.json()[u'geneTable'].split("\t")
    #remove space or newline at the end
    return (decoded)[:-1]

def speciesDefine():
    if args.species.upper() == "RICE":
        species="riceknet"
    elif args.species.upper() == "WHEAT":
        species="wheatknet"
    elif args.species.upper() == "ARABIDOPSIS" or species == "ARA":
        species="araknet"
    print("Chosen knet is " + species)
    return species

def splitNetworkViewUrls(genes, network_view):
    """Splits the network view & keeps only netowrk URLs that match with the gene IDs
    REQUIRES: gene list & network view list
    RETURNS: the updated network view  list
    """
    splitNetworkView = [i.split("list=", 1)[1] for i in network_view]  #Split the network network_view to find matches
    splitNetworkView = [i.split("&", 1)[0] for i in splitNetworkView]
    splitNetworkView = [i.upper() for i in splitNetworkView]
    networkMatchIndex = [splitNetworkView.index(i) for i in genes]
    return [network_view[i] for i in networkMatchIndex]


def knetScorer(genes, species, keyw):
    """ Returns the KnetMiner JSON table containing the KnetScore with successful requests (containing the gene ID and keyword combination given)
        REQUIRES: genes, species ID, and keyword list
        RETURNS: decoded KnetMiner JSON table """

    genestr=(",").join(genes)
    link="http://knetminer.rothamsted.ac.uk/{}/genome?".format(species)
    parameters={"keyword":keyw, "list":genestr}
    r=requests.get(link, params=parameters)
    decoded = decode(r)
    return decoded

def queryAllKnetScorer(species, keyw):
    """ Returns the KnetMiner JSON table containing the KnetScore, but instead pings KnetMiner for ALL genes related to he keyword (takes longer)
        REQUIRES: genes, species ID, and keyword list
        RETURNS: decoded KnetMiner JSON table """

    print("\n\nGoing to query knetminer for ALL returning results and then filter them\n")
    print("This may take a while, so please be patient\n")
    link="http://knetminer.rothamsted.ac.uk/{}/genome?keyword={}".format(species, keyw)
    print("The API request being performed is: {}".format(link))
    r=requests.get(link)
    decoded = decode(r)
    return decoded


def summary():
    """ Searches KnetMiner for the provided keywords & genes, truncating down to only the most relevant information.
        REQUIRES: User-provided arguments.
        RETURNS: Outputs a dataframe containing the matching genes, chromosome score(s), position, & their KnetMiner API URLs.
    """
    with open(args.keywords, "r") as fk:
        pheno=[]
        for line in fk:
            pheno.append(line.rstrip())
        summary=pd.read_csv(args.genes, sep="\t", header=None)
        summary.rename (columns={
                                 0:"GENE"
                                 }, inplace=True )
        genes = list(summary["GENE"])
        startingLen = len(genes)
        #creating knetminer genepage urls.
        network_view=[]
        for i, keyword in enumerate(pheno):
            if ' ' in keyword:
                pheno[i] = "\"" + keyword + "\"" # Fixing git issue #424

        keyw="%20OR%20".join("{}".format(i) for i in pheno)

        #define species
        species = speciesDefine()
        resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY)) # Set stack limit to infinity, so we can use as much of our resources as needed; if needed
        print("\n\n\nPlease wait while I get your KnetMiner API URLs, this may take a while...")
        for i in genes:
            link="http://knetminer.rothamsted.ac.uk/{}/genepage?list={}&keyword={}".format(species, i, keyw)
            network_view.append(link) # We don't need ot ensure the URL works at this stage as we'll filter by gene name later anyway. This will save time.

        #obtaining knetscores for genes
        print("\nYour provided traits are as follows:\n\n")
        print(*pheno, sep=", ") # Collect all positional arguments into tuple and seperate by commas
        if len(genes) <= 100:
            decoded = knetScorer(genes, species, keyw)
        elif len(genes) <= 200 and len(pheno) <= 10:
            decoded = knetScorer(genes, species, keyw)
        elif len(genes) >= 450:
            decoded = queryAllKnetScorer(species, keyw)
        else:
            decoded = queryAllKnetScorer(species, keyw)

        print("Filtering results, please wait...")
        genetable = np.array(decoded).reshape(len(decoded)//9, 9) #tabulate genetable into 9 columns.
        genetable = pd.DataFrame(genetable[1:, :], columns = genetable[0, :])
        genesUpperList = list(map(str.upper, genes)) # Make the genes uppercase
        genetable = genetable.loc[genetable[u'ACCESSION'].isin(genesUpperList)] # Update the table so we only have matching genes

        knetgenes, knetscores = list(genetable[u'ACCESSION']), list(genetable[u'SCORE'])
        knetchro, knetstart = list(genetable[u'CHRO']), list(genetable[u'START'])
        genes_ordered = set(genesUpperList).intersection(knetgenes) # Only keep matching genes
        genes_ordered = list(genes_ordered)

        updatedNetworkView = splitNetworkViewUrls(genes_ordered, network_view)

        filtered_summary = pd.DataFrame(columns=[u'ACCESSION'])
        filtered_summary[u'ACCESSION'] = genes_ordered
        filtered_summary = filtered_summary.merge(genetable, how = 'inner', on= [u'ACCESSION'])
        filtered_summary[u'ACCESSION'] = filtered_summary[u'ACCESSION'].astype(str)

        knetdict=dict(zip(knetgenes, knetscores)) # Map the genes to SNPs via a dictionary.
        if len(genes) <= 5:
            print("\n\nDisplaying knetscores for 5 genes.\n")
            pprint.pprint(list(islice(knetdict.items(), len(knetdict.items()))))
        else:
            print("\n\nDisplaying the knetscore for the top 5 genes:\n")
            pprint.pprint(list(islice(knetdict.items(), 5)))

        filtered_summary['Network View URL'] = updatedNetworkView

        filtered_summary = filtered_summary.drop(filtered_summary.columns[[1, 7, 8]], axis=1)
        filtered_summary.columns = ['Accession ID', 'Gene Name', 'Chromosome', 'Start position', 'TaxID', 'KnetScore', 'Network View URL']

        print("\n\nOrdering genes based on KnetScore, one moment...\n")
        filtered_summary[u'KnetScore'] = filtered_summary[u'KnetScore'].astype(float)
        filtered_summary.sort_values('KnetScore', ascending=False, inplace=True)
        print("Writing results out now...\n")
        if args.output is None:
            filtered_summary.to_csv("results.txt", sep="\t", index=False)
            print("We're Finished! Your results are in: {}/{}_output/results.txt".format(os.getcwd(), str(args.genes)[:-4]))
        else:
            filtered_summary.to_csv(args.output, sep="\t", index=False)
            print("We're Finished! Your results are in: {}".format(args.output))
        print("\n\nIn total, {}/{} genes were returned by KnetMiner.\n".format(len(genes_ordered), startingLen))


def main():

    if args.output is None:
        try:
            print("Creating directory to output results")
            mkfolder()
        except:
            raise

    try:
        print("\n\nParsing your data & arguments...")
        summary()
    except:
        raise

if __name__ == "__main__":
    # User args
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', "--genes", help="Name of plain text file containing a list of genes.", type=str)
    parser.add_argument('-k', "--keywords", help="a plain text file containing description of phenotypes of interest line by line")
    parser.add_argument('-s', "--species", help="Choose from 3 species; rice, wheat, or arabidopsis. Type the name for the respective species i.e. arabidpsis for  (or ara) arabidpsis, rice for rice, etc.", type=str)
    parser.add_argument('-o', "--output", help="Specify the output file you'd like to save your file in. If not provided, it'll save itself in the same place where your gene list file is. Please enter the full path", type=str, required=False)
    args = parser.parse_args()
    main()
    exit
