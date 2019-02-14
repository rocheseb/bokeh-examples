# code from Tony's answer on https://stackoverflow.com/questions/37965669/how-do-i-link-the-crosshairtool-in-bokeh-over-several-plots/54691899#54691899

from bokeh.models import CustomJS, CrosshairTool
from bokeh.plotting import figure, show, curdoc
from bokeh.layouts import gridplot
import numpy as np

def addLinkedCrosshairs(plots):
	"""
	plots: list of figures
	"""
    js_move = '''   start = fig.x_range.start, end = fig.x_range.end
                    if(cb_obj.x>=start && cb_obj.x<=end && cb_obj.y>=start && cb_obj.y<=end)
                        { cross.spans.height.computed_location=cb_obj.sx }
                    else { cross.spans.height.computed_location = null }
                    if(cb_obj.y>=start && cb_obj.y<=end && cb_obj.x>=start && cb_obj.x<=end)
                        { cross.spans.width.computed_location=fig.plot_height-cb_obj.sy  }
                    else { cross.spans.width.computed_location=null }'''
    js_leave = '''cross.spans.height.computed_location=null; cross.spans.width.computed_location=null'''

    figures = plots[:]
    for plot in plots:
        crosshair = CrosshairTool(dimensions = 'both')
        plot.add_tools(crosshair)
        for figure in figures:
            if figure != plot:
                args = {'cross': crosshair, 'fig': figure}
                figure.js_on_event('mousemove', CustomJS(args = args, code = js_move))
                figure.js_on_event('mouseleave', CustomJS(args = args, code = js_leave))