#!/usr/bin/python
# -*- coding: utf-8 -*-

import toolbox
import templater

import sys, os, re, codecs, urllib
import numpy as np
import matplotlib.pyplot as plt

from math import pi, log
from collections import OrderedDict

from bokeh.plotting import figure, ColumnDataSource, save, reset_output
from bokeh.models import Circle, FixedTicker, HoverTool, OpenURL, TapTool
from bokeh.embed import components

# ===========================================================================================

class Mlplot(object):

    """
    Plots a subset of genes/transcripts RNA-Seq expression data
    using the matplotlib library.
    """

    def __init__(self, timepoints, ticks):
        self.timepoints = [float(x) for x in timepoints]
        self.ticks = ticks


    # NOTE: cross-SANITIZE lengths of: ticks, timepoints, expression lists (in dicts)
    # and think if its necessary to split "name" into "filename" & "titlename".
    def plot_mpl_figure(self, subset, name, mode="semilogy", savelocation=os.path.expanduser("~")):

        """
        Generates matplotlib static figures from subsets of differential expressed
        genes/transcripts over a given timecourse experiment. 
        """

        plt.clf()
        plt.title(name)

        if mode == "linear" or mode == "semilogy":
            plt.xlabel("Time points")
        else:
            plt.xlabel("Time points (log)")

        if mode == "linear" or mode == "semilogx":
            plt.ylabel("normalized expression counts")
        else:
            plt.ylabel("log"+r'$\mathregular{_{normalized\ expression\ counts}}$')
  

        plt.xlim(0, self.timepoints[-1])
        plt.xticks(rotation=65)
        plt.xticks(self.timepoints, self.ticks)


        for gene in subset.keys():
            if mode == "linear":
                plt.plot(self.timepoints, subset[gene])
            elif mode == "loglog":
                plt.loglog(self.timepoints, subset[gene])
            elif mode == "semilogx":
                plt.semilogx(self.timepoints, subset[gene])
            elif mode == "semilogy":
                plt.semilogy(self.timepoints, subset[gene])
            else:
                print "Wrong matplotlib axis-mode selected!"
                sys.exit()


        plt.savefig(os.path.join(savelocation, name))
        

# ===========================================================================================


class Blur(object):

    """
    Creates some nice interactive plots for subsets of genes/transcripts
    RNA-Seq expression data by making use of the bokeh library.
    """

    def __init__(self, timepoints, ticks):
        self.timepoints = [float(x) for x in timepoints]
        self.ticks = [float(x) for x in ticks]

 
    def generate_interactive_bokeh_plot(self, subset, name, savelocation, annots=None, plus=None, portability="web"):

        """
        Generates interactive bokeh plots along with (optional) annotation and enrichment reports.
        """

        # PLOT CONFIG (NOTE: maybe expose (init) some of the configs later? ex. axis labels, sizes, etc.)
        # ----------------------------------------------------------------------------------------------------------
        TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select,resize"

        plot = figure(tools=TOOLS, x_axis_label="Time points (h)", 
                                   y_axis_label="normalized expression counts")

        plot.plot_width = 800
        plot.plot_height = 800

        plot.title = name

        plot.title_text_font_size = "18pt"
        plot.title_text_color = "olive"   
        plot.title_text_font = "times"
        plot.title_text_font_style = "italic"

        # AXIS (hardcoded)
        plot.xaxis[0].ticker=FixedTicker(ticks=self.ticks)
        plot.xaxis.bounds = (0, self.timepoints[-1])

        plot.xaxis.major_label_orientation = pi/float(2.5)
        # ----------------------------------------------------------------------------------------------------------

        colour_list = toolbox.get_spaced_colors(len(subset))
        c = 0

        for gene in subset.keys():

            if annots != None:
                labelextra = [annots[gene][0].strip() for x_, y_ in zip(self.timepoints, subset[gene])]
            else:
                labelextra = ["" for x_, y_ in zip(self.timepoints, subset[gene])]


            cds = ColumnDataSource(
                data=dict(
                    x=self.timepoints,
                    y=subset[gene],
                    label=[gene for x_, y_ in zip(self.timepoints, subset[gene])],
                    labelextra = labelextra
                )
            )

            # PLOTARAMA
            plot.line("x","y", source=cds, color=colour_list[c])
            circle = Circle(x='x', y='y', line_color=None, fill_color=colour_list[c])
            c += 1
            circle_renderer = plot.add_glyph(cds, circle)


            # HOVER control
            # -----------------------------------------------------------------------------------
            if annots != None:

                if annots[gene][0].strip() != "": 

                    tooltips = """
                                <div style="width:350px">
                                <b> @label </b><br/>
                                <i><u>annotations:</u></i><br/> @labelextra    
                                </div>
                    """
                else:
                    tooltips = """
                            <div style="width:350px">
                            <b> @label </b><br/>
                            </div>
                    """


            else:
                tooltips = """
                            <div style="width:350px">
                            <b> @label </b><br/>
                            </div>
                """

            plot.add_tools( HoverTool(tooltips=tooltips, renderers=[circle_renderer]))

        # ====================================================== #
        #                        TEMPLATING                      #
        # ====================================================== #

        script, div = components(plot)


        # process "name" here to get "title"
        title = name
 

        # If an annotation or enrichment dictionary is not supplied w/ the
        # methods parameters feed a blank one to the html template renderer.
        if annots == None:
            annots = {}

        if plus is None:
            plus == {}

        # Create the main html page scaffold 
        scaffold = templater.Templater(script, div, title, annots)


        # ====================================================
        if portability == "batch":
            path = os.path.join(savelocation, "static/")
            try: 
                os.makedirs(path)
            except OSError:
                if not os.path.isdir(path):
                    raise

            cssfile = urllib.URLopener()
            cssfile.retrieve("https://cdn.pydata.org/bokeh/release/bokeh-0.11.1.min.css",
                              os.path.join(path, "bokeh-0.11.1.min.css"))
            jsfile = urllib.URLopener()
            jsfile.retrieve("https://cdn.pydata.org/bokeh/release/bokeh-0.11.1.min.js",
                             os.path.join(path, "bokeh-0.11.1.min.js"))



        # If a dictionary of enrichment dataframes is
        # available, pass it along...
        if plus is not None:
            html = scaffold.render_main_page(portability, plus)
        else:
            html = scaffold.render_main_page(portability)

    
        # WRITE IT OUT    
        # --------------------------------------------------------------------------
        filename = os.path.join(savelocation, name+".html")

        # better to save it with the latin-1 charset because wiggly 
        # characters tend to sneak through annotations and they can be a pain...
        with codecs.open(filename, encoding='latin-1', mode="w") as f:
            f.write(html)

        reset_output(plot)    # resets plot data and avoids file balloning when iterating


