from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Button
from bokeh.layouts import gridplot, widgetbox

from random import random, choice

import numpy as np

my_data = {1:{'x':[],'y':[],'colo':[],'size':[]}}

kelly_colors = [ 	'#F3C300','#875692', '#F38400', '#A1CAF1','#BE0032', '#C2B280', '#848482','#008856', '#E68FAC', '#0067A5',
				 	'#F99379', '#604E97', '#F6A600','#B3446C', '#DCD300', '#882D17','#8DB600', '#654522', '#E25822','#2B3D26',		]

x = np.arange(0,50,0.1)

def rand_dict():

	rand_x = [choice(x) for i in range(7)]

	return {'x':rand_x,'y':np.array([random()*100 for i in rand_x]),'colo':np.array([choice(kelly_colors) for i in rand_x]),'size':np.array([(5+int(random()*50)) for i in rand_x])}

def add_stuff():

	global my_data

	my_data[max(my_data.keys())+1] = rand_dict()

	make_doc()

def change_stuff():

	global my_data

	myfig = curdoc().select_one({"name":"myfig"})

	for i,rend in enumerate(myfig.renderers):
		try:
			rend.data_source
		except AttributeError:
			pass
		else:
			my_data[i+1] = rand_dict()
			rend.data_source.data.update(my_data[i+1])

def clear_stuff():

	global my_data

	my_data = {1:{'x':[],'y':[],'colo':[],'size':[]}}

	make_doc()

def make_doc():

	curdoc().clear()

	myfig = figure(plot_width=1000,plot_height=800,outline_line_alpha=0,name='myfig')
	myfig.x_range.start = -5
	myfig.x_range.end = 55
	myfig.y_range.start = -10
	myfig.y_range.end = 110

	myfig.renderers = []

	add_button = Button(label='add stuff',width=100)
	change_button = Button(label='change stuff',width=100)
	clear_button = Button(label='clear stuff',width=100)

	add_button.on_click(add_stuff)
	change_button.on_click(change_stuff)
	clear_button.on_click(clear_stuff)

	grid = gridplot([[myfig,widgetbox(add_button,change_button,clear_button)]],toolbar_location=None)

	curdoc().add_root(grid)

	update_doc()

def update_doc():

	myfig = curdoc().select_one({"name":"myfig"})

	for key in my_data:
		myfig.scatter(x='x',y='y',color='colo',size='size',source=ColumnDataSource(data=my_data[key]))

curdoc().title = 'mytitle'

make_doc()
