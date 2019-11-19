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
# import grequests
import resource
from itertools import islice
import pprint


def mkfolder():
    '''Create a folder for each gapit results, copy result.csv and reference into that directory.
    All results will then be generated within it. The main function will take the script back into parent.'''
    print("Commenced at {}".format(datetime.datetime.now()))
    folder=str(args.file)[:-4] + "_output"
    if os.path.exists(folder):
        shutil.rmtree(folder)
        os.mkdir(folder)
        shutil.copy(args.file, folder)
        shutil.copy(args.list, folder)
        os.chdir(folder)
    else:
        os.mkdir(folder)
        shutil.copy(args.file, folder)
        shutil.copy(args.list, folder)
        os.chdir(folder)

def decode(r):
    if not r.ok:
            r.raise_for_status()
            sys.exit()
    else:
        print("request successful")

    decoded=r.json()[u'geneTable'].split("\t")
    #remove space or newline at the end
    return (decoded)[:-1]

def summary():
    '''Search on knetminer using information provided and truncate down to only relevant info'''
    with open(args.file, "r") as fk:
        pheno=[]
        for line in fk:
            pheno.append(line.rstrip())
        summary=pd.read_csv(args.list, sep="\t", header=None)
        summary.rename (
                        columns={
                            0:"GENE"
                        }, inplace=True )
        genes = list(summary["GENE"])
        startingLen = len(genes)

        #creating knetminer genepage urls.
        network_view=[]
        for i, keyword in enumerate(pheno):
            if ' ' in keyword:
                pheno[i] = "\"" + keyword + "\""


        keyw="%20OR%20".join("{}".format(i) for i in pheno)

        #define species
        args.species = args.species.upper()
        if args.species == "RICE":
            species="riceknet"
        elif args.species == "WHEAT":
            species="wheatknet"
        elif args.species == "ARABIDOPSIS" or args.species == "ARA":
            species="araknet"
        print("Chosen species is " + species)
        resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY)) # Set stack limit to infinity, so we can use as much resources as needed
        for i in genes:
            link="http://knetminer.rothamsted.ac.uk/{}/genepage?list={}&keyword={}".format(species, i, keyw)
            r=requests.get(link)
            network_view.append(r.url)

        #obtaining knetscores for genes
        print("Your provided traits are as follows:")
        pprint.pprint([p for p in pheno])
        if len(genes) < 450:
            print("The genes provided by user:")
            genestr=(",").join(genes)
            print(genestr)
            link="http://knetminer.rothamsted.ac.uk/{}/genome?".format(species)
            parameters={"keyword":keyw, "list":genestr}
            r=requests.get(link, params=parameters)
            #check if requests is successful
            decoded = decode(r)
        elif len(genes) > 450:
            print("Gene length is over 450, will query knetminer for ALL returning results and then filter them instead")
            link="http://knetminer.rothamsted.ac.uk/{}/genome?keyword={}".format(species, keyw)
            r=requests.get(link)
            decoded = decode(r)

        print("Filtering results, please wait...")
        colnum=9
        #tabulate genetable into 9 columns.
        genetable=np.array(decoded).reshape(len(decoded)//colnum, colnum)
        genetable=pd.DataFrame(genetable[1:,:], columns=genetable[0,:])
        genesUpper = list(map(str.upper, genes)) # Make the genes uppercase
        genetable = genetable.loc[genetable[u'ACCESSION'].isin(genesUpper)] # Update the table so we only have matching genes

        knetgenes=list(genetable[u'ACCESSION'])
        # Only keep matching genes
        genes = list(filter(lambda x: x not in genes, knetgenes))
        knetscores=list(genetable[u'SCORE'])
        knetchro=list(genetable[u'CHRO'])
        knetstart=list(genetable[u'START'])


        #Split the network network_view to find matches
        splitNetworkView = [i.split("list=", 1)[1] for i in network_view]
        splitNetworkView = [i.split("&", 1)[0] for i in splitNetworkView]
        splitNetworkView = [i.upper() for i in splitNetworkView]
        networkMatchIndex = [splitNetworkView.index(i) for i in genes]
        updatedNetworkView = [network_view[i] for i in networkMatchIndex]
        filtered_summary = pd.DataFrame({'GENE':genes})

        #map genes to snps via a dictionary.
        knetdict=dict(zip(knetgenes, knetscores))
        if len(genes) < 20:
            print("Displaying knetscores for every gene.")
            pprint.pprint(knetdict)
        else:
            print("Displaying a snippet of your knetscores for every gene:")
            pprint.pprint(list(islice(knetdict.items(), 20)))
        ordered_score=[]
        for index, i in enumerate(genes):
            #convert gene id to upper case to avoid sensitivity issues.
            i=i.upper()
            try:
                ordered_score.append(knetdict[i])
            except KeyError:
                print("Gene " + i + " with index " + index + "not found in the KnetMiner dictionary")
                pass # Skip any keys that shouldn't be present

        filtered_summary[u'knetscore'] = ordered_score
        filtered_summary[u'chromosome'] = knetchro
        filtered_summary[u'start_position'] = knetstart
        filtered_summary[u'network_view'] = updatedNetworkView
        print("These are the genepage urls. They're also available in results.txt.")
        for i in updatedNetworkView:
            print(str(i))
        print("Ordering genes based on KnetScore...\n")
        filtered_summary[u'knetscore'] = filtered_summary[u'knetscore'].astype(float)
        filtered_summary.sort_values('knetscore', ascending=False, inplace=True)
        print("Writing results out now")
        if args.output is None:
            filtered_summary.to_csv("results.txt", sep="\t", index=False)
            print("Finished! Your results are in: {}_output/results.txt".format(os.getcwd()))
        else:
            filtered_summary.to_csv(args.output, sep="\t", index=False)
            print("Finished! Your results are in: {}".format(args.output))
        print("In total, {}/{} genes were returned by KnetMiner".format(startingLen, len(genes)))


def main():

    if args.output is None:
        try:
            print("creating directory to output results")
            mkfolder()
        except:
            raise

    try:
        print("Searching with Knetminer for information relating to the genes.")
        summary()
    except:
        raise

    os.remove(args.list)
    os.remove(args.file)


if __name__ == "__main__":
    #creating parameters for the end-user.
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Name of plain text file containing a list of genes.", type=str)
    parser.add_argument("list", help="a plain text file containing description of phenotypes of interest line by line")
    parser.add_argument("species", help="Choose from 3 species; rice, wheat, or arabidopsis. Type the name for the respective species i.e. arabidpsis for  (or ara) arabidpsis, rice for rice, etc.", type=str)
    parser.add_argument("output", help="Specify the output file you'd like to save your file in. If not provided, it'll save itself in the same place where your gene list file is. Please enter the full path", type=str)
    args = parser.parse_args()

    main()

    print("The entire pipeline finished at:")
    print(datetime.datetime.now())

    exit
