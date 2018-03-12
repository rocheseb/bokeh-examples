from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import Button,Legend
from bokeh.layouts import gridplot, Column
from bokeh.palettes import Category20_20
from functools import partial

from random import random,choice
import numpy as np

doc = curdoc()

x=range(3)

fig1 = figure(plot_width=250,plot_height=250)
fig1.renderers = []
fig2 = figure(plot_width=250,plot_height=250)
fig2.renderers = []
dum_fig = figure(plot_width=250,plot_height=500,outline_line_alpha=0)
legend = Legend(click_policy='hide',border_line_alpha=0,location='top_left')
dum_fig.renderers = [legend]
# set a range of values that will not include any data
dum_fig.x_range.end = 1005
dum_fig.x_range.start = 1000

button = Button(label="add a line",width=100)

def add_line():
	colo = choice(Category20_20)
	randname = str(random())
	line1 = fig1.line(x,[random() for i in x],color=colo,line_width=3,legend=randname)
	line2 = fig2.line(x,[random() for i in x],color=colo,line_width=3)
	line1.on_change('visible',partial(share_visible,line1=line1,line2=line2))
	update_legend(line1)

button.on_click(add_line)

def share_visible(attr,old,new,line1,line2):
	line2.visible = line1.visible

def update_legend(line1):
	leg1 = fig1.legend[0]
	legend.items += leg1.items
	dum_fig.renderers += [line1]
	leg1.visible = False
	fig1.renderers = [i for i in fig1.renderers if i!=leg1]

grid = gridplot([[button],[Column(fig1,fig2),dum_fig]],toolbar_location=None)

doc.add_root(grid)