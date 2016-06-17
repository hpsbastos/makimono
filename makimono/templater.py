#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, re
import pandas as pd
from jinja2 import Template
from bokeh.resources import INLINE

pd.set_option('display.max_colwidth', -1)
pd.options.mode.chained_assignment = None  # default='warn'

class Templater(object):

    def __init__(self, script, div, title, annot):
        self.script = script
        self.div = div
        self.title = title
        self.annots = annot

    # NOTE: currently this method overrides "process_enrichment_dict()" 
    #       regarding the display of missing (None) enrichment info.
    def render_main_page(self, portability, plus = None):

        """
        Renders the main page template for a plot and association expression
        information: gene/transcript list, annotations, (GO/KEGG) enrichment
        results.     
        """

        # TODO: make css customizing accessible
        csstables = '''
                    <style type="text/css">
                        .etables {
                            dir: ltr;
                            width: 1200px;
                        }
                    </style>
                    '''

        # Hardcoded, but (for the time being) it is for the best.
        # NOTE: if changed in the future, remember to keep paths relative.
        if portability == "batch":
            css_resources = '<link rel="stylesheet" href="static/bokeh-0.11.1.min.css" type="text/css" />'
            js_resources = '''
                            <script type="text/javascript" src="static/bokeh-0.11.1.min.js"></script>
                                <script type="text/javascript">
                                    Bokeh.set_log_level("info");
                                </script>
                           '''

        elif portability == "web":

            css_resources = '''
                <link rel="stylesheet" href="https://cdn.pydata.org/bokeh/release/bokeh-0.11.1.min.css" type="text/css" />'''+csstables
            js_resources = '''
                <script type="text/javascript" src="https://cdn.pydata.org/bokeh/release/bokeh-0.11.1.min.js"></script>
                <script type="text/javascript">
                    Bokeh.set_log_level("info");
                </script>

                           '''
        # or "full", meaning full portability, but at a cost of increased filesize
        else:            
            js_resources = INLINE.render_js()
            css_resources = INLINE.render_css()

    # ----------------------------------------------------------------------------

        if plus is not None:

            bp = plus['bp']
            mf = plus['mf']
            cc = plus['cc']
            kegg = plus['kegg']

            # a small hack to pass along the significance 
            # level (filter for GO enrichments)
            alpha = plus['alpha']
        else:
            bp = None
            mf = None
            cc = None
            kegg = None
            alpha = 0.05


        t_bp, t_mf, t_cc, t_kegg = self.process_enrichment_dict(bp, mf, cc, kegg, alpha)


        if bp is not None or mf is not None or cc is not None:
            goheader = '''<p style="font-size:20px; font-weight: bold;">GO term enrichment</p>'''
        else:
            goheader = ""


        if bp is not None:
            bp_info = '''
            <span style="font-size:16px; font-weight: bold;">Biological Process</span>
            {% block table1a %}
            {{ tablegobp }}
            {% endblock %}
            <br/>
            '''

        else:
            bp_info = ""         

        if mf is not None:
            mf_info = '''        
            <span style="font-size:16px; font-weight: bold;">Molecular Function</span>
            {% block table1b %}
            {{ tablegomf }}
            {% endblock %}
            <br/>
            '''
        else:
            mf_info = ""

        if cc is not None:
            cc_info = '''        
            <span style="font-size:16px; font-weight: bold;">Cellular Component</span>
            {% block table1c %}
            {{ tablegocc }}
            {% endblock %}
            <br/>
            <br/>
            '''
        else:
            cc_info = ""

        if kegg is not None:
            kegg_info = '''
            <span style="font-size:20px; font-weight: bold;">KEGG pathways enrichment</span>
            {% block table2 %}
            {{ tablekegg }}
            {% endblock %}
            <br/>
            '''
        else:
            kegg_info = ""

    # ----------------------------------------------------------------------------

        template = Template('''<!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="latin-1">
                <title>{{ title }}</title>
                {{ js_resources }}
                {{ css_resources }}
                {{ script }}
            </head>
            <body>
                {{ div }}
                <br/>

                <br/>
                '''+goheader+bp_info+mf_info+cc_info+kegg_info+
                ''' 
                {% block table3 %}
                {{ annots }}
                {% endblock %}

            </body>
        </html>
        ''')

        html = template.render(js_resources=js_resources,
                               css_resources=css_resources,
                               script=self.script,
                               div=self.div,
                               title = self.title,
                               tablegobp = t_bp,
                               tablegomf = t_mf,
                               tablegocc = t_cc,
                               tablekegg = t_kegg,                           
                               annots = self.render_gene_table(),
                               )
        return html
 

    # make Jinja2 table template for gene/transcript annotation data/list
    # NOTE: Currently all available annotations per gene/transcript are
    # dumped into a single cell. TODO: ponder the best way to improve that!
    # Maybe a scarse matrix-like table via pandas dataframe? 
    # --------------------------------------------------------------------
    def render_gene_table(self):

        """
        Renders the available annotations for the genes/transcripts being
        plotted into 1st column: gene/transcript identifier; 2nd column:
        all available annotations.
        """

        tablegene = Template('''<span style="font-size:20px; font-weight: bold;">
                                Genes/transcripts</span>
                            <table dir="ltr" width="1200" border="1">                   
                            <thead>
                                <tr>
	                                <th scope="col">Identifier</th>
		                            <th scope="col">Annotations</th>    
                                </tr>
                            </thead>
                            <tbody>
                                {% for key in genedata: %}
                                    {% if genedata[key][0].strip() !="": %}
                                    <tr>
                                        <td>
                                        {{ key }}
                                        </td>
                                        <td>
                                        {{ genedata[key][0].strip() }}
                                        </td>
                                    </tr>
                                    {% endif %}                    
                                {% endfor %}
                                <br/>

                            </tbody>
                        </table>
                        ''')

        if len(self.annots) > 0:
            table = tablegene.render(genedata=self.annots)
        else:
            table = Template("").render()

        return table



    # TODO: Evaluate if displaying "No significant enriched terms found!"
    #       is of worth, or just leave blank... **kwargs...it?
    def process_enrichment_dict(self, gobp, gomf, gocc, kegg, alpha):

        """
        Method receives dataframes containing GO/KEGG enrichment results and
        converts them into html tables.
        """

        if gobp is not None:
            bpslice = gobp.loc[gobp['elimFisher'] < alpha]
            if len(bpslice) > 0:
                bpslice["GO.ID"] = bpslice["GO.ID"].map(lambda x: '<a href="http://amigo.geneontology.org/amigo/term/'+str(x)+'" target="_blank">'+str(x)+'</a>')
                gobptable = bpslice.to_html(index=False, classes="etables", escape=False)
            else:
                gobptable = self.not_found_response()
        else:
            gobptable = self.not_found_response()

        if gomf is not None:
            mfslice = gomf.loc[gomf['elimFisher'] < alpha]
            if len(mfslice) > 0:
                mfslice["GO.ID"] = mfslice["GO.ID"].map(lambda x: '<a href="http://amigo.geneontology.org/amigo/term/'+str(x)+'" target="_blank">'+str(x)+'</a>')
                gomftable = mfslice.to_html(index=False, classes="etables", escape=False)
            else:
                gomftable = self.not_found_response()
        else:
            gomftable = self.not_found_response()

        if gocc is not None:
            ccslice = gocc.loc[gocc['elimFisher'] < alpha]
            if len(ccslice) > 0:
                ccslice["GO.ID"] = ccslice["GO.ID"].map(lambda x: '<a href="http://amigo.geneontology.org/amigo/term/'+str(x)+'" target="_blank">'+str(x)+'</a>')
                gocctable = ccslice.to_html(index=False, classes="etables", escape=False)
            else:
                gocctable = self.not_found_response()
        else:
            gocctable = self.not_found_response()

        if kegg is not None:
            # changes the column order of the KEGG enrichment results
            kegg["KEGGID"] = kegg["KEGGID"].map(lambda x: '<a href="http://www.genome.jp/dbget-bin/www_bget?pathway:map'+str(x)+'" target="_blank">'+str(x)+'</a>') 
            cols = ['KEGGID', 'Term', 'Size', 'Count', 'ExpCount', 'OddsRatio', 'Pvalue']
            keggtable = kegg[cols].to_html(index=False, classes="etables", escape=False)
        else:
            keggtable = self.not_found_response()


        return gobptable, gomftable, gocctable, keggtable


    # render this line when no GO terms found to be enriched 
    def not_found_response(self):

        tablego = Template('<br/>No significant enriched terms found!<br/>')
        table = tablego.render()
        return table
