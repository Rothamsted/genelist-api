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
        counter, total = 0, 0
        for i in genes:
            link="http://knetminer.rothamsted.ac.uk/{}/genepage?list={}&keyword={}".format(species, i, keyw)
            if len(genes) > 100:
                network_view.append(link) # We don't need ot ensure the URL works at this stage as we'll filter by gene name later anyway. This will save time.
            else:
                r=requests.get(link)
                network_view.append(r.url)
                counter+=1
                total+=1
                if counter == 50:
                    print('Performed {} requests out of {}'.format(total, len(genes)))
                    counter = 0

        #obtaining knetscores for genes
        print("Your provided traits are as follows:\n\n")
        print(*pheno, sep=", ") # Collect all positional arguments into tuple and seperate by commas
        if len(genes) < 450:
            genestr=(",").join(genes)
            link="http://knetminer.rothamsted.ac.uk/{}/genome?".format(species)
            parameters={"keyword":keyw, "list":genestr}
            r=requests.get(link, params=parameters)
            #check if requests is successful
            decoded = decode(r)
        elif len(genes) > 450:
            print("\n\nGene length is over 450, I'll query knetminer for ALL returning results and then filter them instead")
            print("This may take a while, so please be patient\n")
            link="http://knetminer.rothamsted.ac.uk/{}/genome?keyword={}".format(species, keyw)
            r=requests.get(link)
            decoded = decode(r)

        print("Filtering results, please wait...")
        genetable=np.array(decoded).reshape(len(decoded)//9, 9) #tabulate genetable into 9 columns.
        genetable = pd.DataFrame(genetable[1:,:], columns=genetable[0,:])
        genesUpper=list(map(str.upper, genes)) # Make the genes uppercase
        genetable=genetable.loc[genetable[u'ACCESSION'].isin(genesUpper)] # Update the table so we only have matching genes

        knetgenes, knetscores = list(genetable[u'ACCESSION']), list(genetable[u'SCORE'])
        knetchro, knetstart = list(genetable[u'CHRO']), list(genetable[u'START'])
        genes = list(filter(lambda x: x not in genes, knetgenes)) # Only keep matching genes

        splitNetworkView = [i.split("list=", 1)[1] for i in network_view]  #Split the network network_view to find matches
        splitNetworkView = [i.split("&", 1)[0] for i in splitNetworkView]
        splitNetworkView = [i.upper() for i in splitNetworkView]
        networkMatchIndex = [splitNetworkView.index(i) for i in genes]
        updatedNetworkView = [network_view[i] for i in networkMatchIndex]
        filtered_summary = pd.DataFrame({'GENE':genes})

        knetdict=dict(zip(knetgenes, knetscores)) # Map the genes to SNPs via a dictionary.
        if len(genes) < 20:
            print("Displaying knetscores for every gene.")
            pprint.pprint(knetdict)
        else:
            print("Displaying a snippet of your knetscores for every gene:")
            pprint.pprint(list(islice(knetdict.items(), 20)))
        ordered_score=[]
        for index, i in enumerate(genes):
            i=i.upper() #convert gene id to upper case to avoid sensitivity issues.
            try:
                ordered_score.append(knetdict[i])
            except KeyError:
                print("Gene " + i + " with index " + index + "not found in the KnetMiner dictionary")
                pass # Skip any keys that shouldn't be present, though we should never arrive at this keyError anyway as we take care of this earlier when filtering the genes

        ordered_score, knetchro = filtered_summary[u'knetscore'], filtered_summary[u'chromosome']
        knetstart, updatedNetworkView = filtered_summary[u'start_position'], filtered_summary[u'network_view']

        if len(updatedNetworkView) < 20:
            print("These are your genepage URLS. They're also available in results.txt.")
            for i in updatedNetworkView:
                pprint.pprint(str(i))

        print("Ordering genes based on KnetScore, one moment...\n")
        filtered_summary[u'knetscore'] = filtered_summary[u'knetscore'].astype(float)
        filtered_summary.sort_values('knetscore', ascending=False, inplace=True)
        print("Writing results out now!")
        if args.output is None:
            filtered_summary.to_csv("results.txt", sep="\t", index=False)
            print("We're Finished! Your results are in: {}/{}_output/results.txt".format(os.getcwd(), str(args.genes)[:-4]))
        else:
            filtered_summary.to_csv(args.output, sep="\t", index=False)
            print("We're Finished! Your results are in: {}".format(args.output))
        print("\n\nIn total, {}/{} genes were returned by KnetMiner".format(len(genes), startingLen))


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
