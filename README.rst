Makimono
--------

Makimono is a python package wrapping (mostly) around the *matplotlib* and *bokeh* 
packages and providing convenient plotting tools to visualize RNA-Seq expression in sets
of interest.  Optionally, GO and/or KEGG enrichment ("interfacing" with the *R* packages *topGO*
and *GOstats*) reports for those sets of interest can also be generated from topGO/GOstats results and incorporated into the makimono package outputs.

===============================================================================

**Current release:** *0.1.3 (alpha)*

Provides basic functionality and basic documentation. Methods and functions are working provided the inputs
are within the expected formats and constraints (onus is on the user -- see more at the end).

**TODO:**
  
- Write tests
- Improve documentation
- Increment/improve exception handling
- Extend functionality with new features
- Re-write old code to integrate as new modules

===============================================================================

**Installation:**

.. code::

  # pip install makimono-0.1.3.tar.gz

or

.. code::

  # pip install makimono

**Usage:**

Refer to the included jupyter python notebooks (see docs folder) for usage examples of the methods and functions in the *makimono* package.

Additionally, the *makimono* package ships with a command line utility, **makisu**  
that allows access to part of the functionally of the package.

 
To use *makisu* on the command line just type::
    
    $ makisu [arguments]


    makisu 
    usage: makisu [-h] -p {mpl,bokeh,bokehplus} -e EXPRESSION -r REPLICATES -t
              TIMEPOINTS [TIMEPOINTS ...] -i INPUT [-a ALPHA]
              [-xk XTICKS [XTICKS ...]] [-m {all,web,batch}] [-o OUTPUTFOLDER]

  Required arguments:

    [-p] plotting mode (options: mpl, bokeh, bokehplus)
    [-e] path to file with RNA-Seq expression counts
    [-r] number of replicates in expression counts file
    [-t] list of experimental time points
    [-i] path [or folder] to file(s) containing lists of genes/transcripts of interest

  Optional arguments:

    [-a] level of significance (to filter enrichment results) -- [defaults to 0.05]
    [-xk] list of ticks for the plot's x-axis -- [defaults to timepoints]
    [-m] plot portability (for bokeh/bokehplus -- options: all, web[default] and batch)
    [-o] folder where to output your plots/reports [defaults to user's home directory]

    

Input files requirements:
======================================================

To use makimono the following files are required:

1. RNA-Seq expression counts.
2. List(s) of subsets of genes/transcripts of interest.

The RNA-Seq expression file should be a tab-separated file where the first column corresponds a gene/transcript identifier with the following columns being the counts for each replicate at each experimental time point.

*e.g.*

.. code::
     
  Cre14.g622075.t1.1   10    5   75   77   39   34   18   25   15   22   21    6   19   13   17   32

         (...)

  Cre10.g467200.t1.1   21   36  320  293  114  111   37   80   63   68   49   61   53   66   66   86

In the example above comes from an experiment with 8 time points and 2 replicates, thus for transcript *Cre14.g622075.t1.1* 10 and 5 are the counts for the two replicates at the first time point, 75 and 77 are the counts for the two replicates at the second time point and so on.  

The file(s) with the genes/transcripts of interest must list one identifier per line and optionally can have additional (tab-separated) annotations on their respective line.  

*e.g.*

.. code::

  Cre01.g053250.t1.1				RING/FYVE/PHD zinc finger superfamily protein
  Cre02.g147150.t1.1

       (...)  
				
  Cre03.g173800.t1.2	PDX2	Pyridoxal kinase	Pyridoxal kinase, involved in vitamin B6 biosynthesis.



Term enrichment reports:
======================================================
(available with the 'bokehplus' plotting mode)

  Term enrichment reports for GO term enrichment and KEGG pathway enrichment can be incorporated into the *bokeh* interactive plots. **Makimono** uses the enrichment result files as produced by the **R** packages *topGO* (for GO term enrichments) and *GOstats* (for KEGG pathways enrichments) to generate these reports. To use these R modules (these need to be installed on the system and) and one should refer to their original documentation or alternatively use (see example in docs folder) the limited and experimental "interface" provided by the module *enricher* packaged with **makimono**.

*e.g.*

*GO term enrichment file sample* (produced by topGO)

.. code::

  GO.ID 	Term   Annotated    Significant   Expected   Rank in classicFisher	classicFisher	elimFisher
  GO:0034450	ubiquitin-ubiquitin ligase activity	       2	2	0	1	3.3e-06	3.3e-06
  GO:0004360	glutamine-fructose-6-phosphate transamin...    1	1	0	4	0.0019	0.0019
  GO:0008478	pyridoxal kinase activity	               2	1	0	6	0.0038	0.0038

*GO term enrichment file sample* (produced by topGO)

*e.g.*

.. code::

  KEGGID	       Pvalue	OddsRatio	           ExpCount	Count	Size	               Term
  00790	  0.00540248514316588	      Inf	0.00540248514316586	    1	  10	Folate biosynthesis



**WARNING**: The current implementation of the *enricher* module relies on a rigid folder/filename structure and convention.

  - Enrichment result files must be of the form: <basename>_enrichment.tsv 
  - Enrichment files must be placed on a rigid folder hierarchy relative to the location of the files with the sets of interest, as in the example shown below.

*e.g.*

.. code::

  .
  ├── 002_{0h=2h=8h=12h=24h=48h}GT{30min=4h}.txt
  ├── 026_{30min}GT{2h}GT{4h=8h=12h=24h=48h}GT{0h}.txt
  ├── 053_{8h=12h=24h=48h}GT{30min=2h=4h}GT{0h}.txt
  ├── 317_{30min=2h=4h=8h=12h=24h=48h}GT{0h}.txt
  ├── goenrich
  │   ├── BP
  │   │   ├── 002_{0h=2h=8h=12h=24h=48h}GT{30min=4h}_enrichment.tsv
  │   │   ├── 026_{30min}GT{2h}GT{4h=8h=12h=24h=48h}GT{0h}_enrichment.tsv
  │   │   ├── 053_{8h=12h=24h=48h}GT{30min=2h=4h}GT{0h}_enrichment.tsv
  │   │   └── 317_{30min=2h=4h=8h=12h=24h=48h}GT{0h}_enrichment.tsv
  │   ├── CC
  │   │   ├── 002_{0h=2h=8h=12h=24h=48h}GT{30min=4h}_enrichment.tsv
  │   │   ├── 026_{30min}GT{2h}GT{4h=8h=12h=24h=48h}GT{0h}_enrichment.tsv
  │   │   ├── 053_{8h=12h=24h=48h}GT{30min=2h=4h}GT{0h}_enrichment.tsv
  │   │   └── 317_{30min=2h=4h=8h=12h=24h=48h}GT{0h}_enrichment.tsv
  │   └── MF
  │       ├── 002_{0h=2h=8h=12h=24h=48h}GT{30min=4h}_enrichment.tsv
  │       ├── 026_{30min}GT{2h}GT{4h=8h=12h=24h=48h}GT{0h}_enrichment.tsv
  │       ├── 053_{8h=12h=24h=48h}GT{30min=2h=4h}GT{0h}_enrichment.tsv
  │       └── 317_{30min=2h=4h=8h=12h=24h=48h}GT{0h}_enrichment.tsv
  └── keggenrich
      ├── 026_{30min}GT{2h}GT{4h=8h=12h=24h=48h}GT{0h}_enrichment.tsv
      ├── 053_{8h=12h=24h=48h}GT{30min=2h=4h}GT{0h}_enrichment.tsv
      └── 317_{30min=2h=4h=8h=12h=24h=48h}GT{0h}_enrichment.tsv

In the example above, the files listing the four sets of interest are at the root directory. Sub-directory **keggenrich/** holds the respective KEGG pathway enrichment result files (for each of the four sets of interest). The **goenrich/** sub-directory holds the enrichment result files for the GO term enrichments for the same four sets of interest. However, there they are further split into three different sub-directories reflecting each orthogonal ontology comprising the GeneOntology.   
