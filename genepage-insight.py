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

def summary():
    '''Search on knetminer using information provided and truncate down to only relevant info'''

    with open(args.list, "r") as fk:
        pheno=[]
        for line in fk:
            pheno.append(line.rstrip())
        summary=pd.read_csv(args.file, sep="\t", header=None)
        summary.rename (
                        columns={
                            0:"GENE"
                        }, inplace=True )
        genes = list(summary["GENE"])


        #creating knetminer genepage urls.
        network_view=[]
        keyw2="+OR+".join("({})".format(i.replace(" ", "+AND+")) for i in pheno)

        #define species
        args.species = args.species.upper()
        if args.species == "RICE":
            species="riceknet"
        elif args.species == "WHEAT":
            species="wheatknet"
        elif args.species == "ARABIDOPSIS" or args.species == "ARA":
            species="araknet"
        print("Chosen species is " + species)
        if len(genes) < 500:
            for i in genes:
                link="http://knetminer.rothamsted.ac.uk/{}/genepage?list={}&keyword={}".format(species, i, keyw2)
                r=requests.get(link)
                network_view.append(r.url)
        elif len(genes) > 500:
            # TODO: logic needs changing to perform batch requests and concat the final dataframe
            genes = genes[:500]
            for i in genes:
                link="http://knetminer.rothamsted.ac.uk/{}/genepage?list={}&keyword={}".format(species, i, keyw2)
                r=requests.get(link)
                network_view.append(r.url)

        #obtaining knetscores for genes
        keyw1="%20OR%20".join("({})".format(i.replace(" ", "+AND+")) for i in pheno)
        print("The traits provided by user:")
        print(keyw1)
        print("The genes provided by user:")
        genestr=(",").join(genes)
        print(genestr)
        link="http://knetminer.rothamsted.ac.uk/{}/genome?".format(species)
        parameters={"keyword":keyw1, "list":genestr}
        r=requests.get(link, params=parameters)

        #check if requests is successful
        if not r.ok:
                r.raise_for_status()
                sys.exit()
        else:
            print("request successful")

        #extract unicode string of geneTable decoded from json
        decoded=r.json()[u'geneTable'].split("\t")
        #remove space or newline at the end
        decoded=(decoded)[:-1]

        colnum=9
        #tabulate genetable into 9 columns.
        genetable=np.array(decoded).reshape(len(decoded)//colnum, colnum)
        genetable=pd.DataFrame(genetable[1:,:], columns=genetable[0,:])

        knetgenes=list(genetable[u'ACCESSION'])
        knetscores=list(genetable[u'SCORE'])
        knetchro=list(genetable[u'CHRO'])
        knetstart=list(genetable[u'START'])

        # Only keep matching genes
        genes = list(filter(lambda x: x not in genes, knetgenes))
        #Split the network network_view to find matches
        splitNetworkView = [i.split("list=", 1)[1] for i in network_view]
        splitNetworkView = [i.split("&", 1)[0] for i in splitNetworkView]
        splitNetworkView = [i.upper() for i in splitNetworkView]
        networkMatchIndex = [splitNetworkView.index(i) for i in genes]
        updatedNetworkView = [network_view[i] for i in networkMatchIndex]
        filtered_summary = pd.DataFrame({'GENE':genes})

        #map genes to snps via a dictionary.
        knetdict=dict(zip(knetgenes, knetscores))
        print("Displaying knetscores for every gene.")
        print(knetdict)
        ordered_score=[]
        for index, i in enumerate(genes):
            #convert gene id to upper case to avoid sensitivity issues.
            i=i.upper()
            try:
                ordered_score.append(knetdict[i])
            except KeyError:
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
        filtered_summary.to_csv("/mnt/c/Users/hearnshawj/results.txt", sep="\t", index=False)


def main():
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
    args = parser.parse_args()

    main()

    print("The entire pipeline finished at:")
    print(datetime.datetime.now())

    exit
