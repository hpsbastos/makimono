#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, re, codecs, json
import pandas as pd

pd.set_option('display.max_colwidth', -1)

"""
Collection of 'orphan' functions, that are either required
by some methods or that are helpful for pipelining.
"""
#TODO: Evaluate elimination/integration of these functions elsewhere.

# ========================================================================================

def read_annotation_file(directory, f):

    """
    Reads and parses a tsv annotation file into "two columns" split:
    identifier(key):annotations(values). -- all available annotations.
    """

    annotDict = {}

    patt = re.compile('^(\S+)\t(.*)', re.IGNORECASE)

    with codecs.open(os.path.join(directory,f), encoding='latin-1') as fh:
        for line in fh:

            m = patt.search(line)
            if m:
                annotDict.setdefault(m.group(1), []).append(m.group(2))

    return annotDict

# ========================================================================================

def process_title(text):

    """
    Processes input filenames -- derived from the ClusterSeq R package
    into plot titles.
    """
    text = re.sub("(GT)", ">", text)
    text = re.sub("^(\d{3})_", "[%s " %(r"\1]\n"), text)

    return text

# ========================================================================================

def get_spaced_colors(n):

    """
    Creates and array of n different colors --  code found at the following link:
    https://www.quora.com/How-do-I-generate-n-visually-distinct-RGB-colours-in-Python
    """
    max_value = 16581375 #255**3
    interval = int(max_value / n)
    colors = [hex(I)[2:].zfill(6) for I in range(0, max_value, interval)]
    
    return [(int(i[:2], 16), int(i[2:4], 16), int(i[4:], 16)) for i in colors]

# ========================================================================================

def process_expression_values(expressionfile, reps):

    """
    Processes a tsv file containing expression counts into a dictionary.
    NOTES: Expects lines to be in the shape: ID A1 ... An ... Z1 ... Zn
           where A-Z are the different of time points (series) and each
           having n replicates. The replicates are then conflated by 
           calculing the average for each observation at time point.
    WARNING: The function also adds +1 to each expression count in order
             to deal with possible ZEROS so it does not tilt-out in a
             logarithmic axis.
    """
    data = {}
    with expressionfile as fh:
        for line in fh:
            token = line.split("\t")
            token = [token[0]] + [int(x.strip())+1 for x in token[1:]]            
            confl = []
            for i in range(1, len(token)-1, reps):
                confl.append( (token[i] + token[i+1])/float(reps) )            
            data[token[0]] = confl    

    return data

# ========================================================================================

def read_tsv(tsvpath, ont):

    """
    Reads enrichment results tsv files (as produced either by GOstats or
    the topGO R packages) into pandas dataframes (including the headers).

    """

    try:
        if ont != "KEGG Pathways":
            df = pd.read_csv(tsvpath, sep="\t")
        else:
            df = pd.read_csv(tsvpath, sep="\t", converters={'KEGGID': lambda x: str(x)})
    except:
        f = os.path.splitext(os.path.basename(tsvpath))[0]
        print "No %s enrichment found for %s!" % (ont, f)
        raise

    return df

# ========================================================================================

# WARNING: Currently relies on a strict folder structure and file name pattern
#          if no enrichment results are being shown probably that structure is
#          not being met (assuming enrichment data is actually available).
def process_enrichment_values(directory, basename, alpha):

    """
    Processes KEGG/GO enrichment results files (produced by GOstats and topGO)
    into a dictionary.
    """
    

    try:
        bp = read_tsv(os.path.join(directory, 'goenrich/BP', 
                              basename+'_enrichment.tsv'), "GO Biological Process")
    except:
        bp = None
        
        
    try:
        mf = read_tsv(os.path.join(directory, 'goenrich/MF', 
                              basename+'_enrichment.tsv'), "GO Molecular Function")
    except:
        mf = None
        
    try:
        cc = read_tsv(os.path.join(directory, 'goenrich/CC',
                              basename+'_enrichment.tsv'), "GO Cellular Component")
    except:
        cc = None
        
        
    try:
        kegg = read_tsv(os.path.join(directory, 'keggenrich', 
                                basename+'_enrichment.tsv'), "KEGG Pathways")
    except:
        kegg = None


    extra = {'bp':bp, 'mf':mf, 'cc': cc, 'kegg':kegg, 'alpha': alpha}

    return extra

# ========================================================================================
