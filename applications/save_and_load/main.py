"""
Example app to save and load a document. The app content must be in one layout object (curdoc() only has one root)
"""

import bokeh
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.model import collect_models
from bokeh.models import Div, Button, Select, Range1d
from bokeh.layouts import gridplot, widgetbox
from bokeh.document import Document

import json
from datetime import datetime
import numpy as np
import os

from random import random, shuffle, choice

app_path = os.path.dirname(__file__)
save_path = os.path.join(app_path,'json_doc')

kelly_colors = [ 	'#F3C300','#875692', '#F38400', '#A1CAF1','#BE0032', '#C2B280', '#848482',
				 	'#008856', '#E68FAC', '#0067A5','#F99379', '#604E97', '#F6A600','#B3446C',
				 	'#DCD300', '#882D17','#8DB600', '#654522', '#E25822','#2B3D26',				]

def save_session():
	'''
	save a json string of the current document, documents saved like this can be loaded later from the app !
	'''

	save_name = '_'.join(str(datetime.now())[:19].split()).replace(':','-')

	np.save(os.path.join(save_path,save_name),curdoc().to_json_string())

	curdoc().select_one({"name":"status_div"}).text = 'Current session saved in:<br>json_doc/'+save_name+'.npy'

	curdoc().select_one({"name":"session_input"}).options = ['']+os.listdir(save_path)

def load_session():
	'''
	load a previously saved session
	'''

	if curdoc().select_one({"name":"session_input"}).value == "":
		curdoc().select_one({"name":"status_div"}).text = 'You need to select a previous session first'
		return

	select_session = curdoc().select_one({"name":"session_input"}).value
	json_string=np.load(os.path.join(save_path,select_session)).item()

	new_doc = Document.from_json_string(json_string)
	new_grid_models = collect_models(new_doc.roots[0])

	for elem in new_grid_models:
		try:
			elem.document = curdoc()
		except AttributeError:
			elem._document =curdoc()

	new_children = new_doc.roots[0].children

	del grid.children

	grid.children = new_children

	# re-attribute the python callbacks to the widgets
	curdoc().select_one({"name":"do_stuff_button"}).on_click(do_stuff)
	curdoc().select_one({"name":"save_button"}).on_click(save_session)
	curdoc().select_one({"name":"clear_button"}).on_click(clear_fig)
	curdoc().select_one({"name":"load_button"}).on_click(load_session)

	# do custom stuff for the update
	curdoc().select_one({"name":"session_input"}).options = ['']+os.listdir(save_path)
	curdoc().select_one({"name":"session_input"}).value = select_session

def do_stuff():

	curfig = curdoc().select_one({"name":"myfig"})

	shuffle(kelly_colors)

	x=np.arange(0,10,0.01)
	x_values = [choice(x) for i in range(20)]

	curfig.scatter(x_values,[random() for i in range(20)],color=kelly_colors,size=10)

def clear_fig():

	curdoc().select_one({"name":"myfig"}).renderers = []
	curdoc().select_one({"name":"status_div"}).text = 'Click the "Do stuff" button to add points'


session_input = Select(title='Previous sessions:',options=['']+os.listdir(save_path),width=240,css_classes=["custom_input"],name="session_input")

save_button = Button(label='Save Session', width=90, css_classes=["custom_button"],name="save_button")
load_button = Button(label='Load Session', width=90, css_classes=["custom_button"],name="load_button")
do_stuff_button = Button(label='Do stuff', width=90, css_classes=["custom_button"],name="do_stuff_button")
clear_button = Button(label='Clear points',width=90, css_classes=["custom_button"],name='clear_button')

save_button.on_click(save_session)
load_button.on_click(load_session)
do_stuff_button.on_click(do_stuff)
clear_button.on_click(clear_fig)

status_text = Div(text='<font size=2 color="teal"><b>Status:</b></font>',name="status_text")
status_div = Div(text='Click the "Do stuff" button to add points',width=300,name="status_div")

space_div1 = Div(text='',height=80)
space_div2 = Div(text='',width=50)
space_div3 = Div(text='',width=50)
line_div1 = Div(text='<hr width="100%"" color="lightblue">',width = 240)
line_div2 = Div(text='<hr width="100%"" color="lightblue">',width = 240)

side_box = gridplot([[space_div1],[session_input],[load_button,space_div2,save_button],[line_div1],[do_stuff_button,space_div3,clear_button],[line_div2],[status_text],[status_div]],toolbar_location=None,css_classes=["side_box"])

fig = figure(plot_width = 900, plot_height=600, name="myfig",outline_line_alpha=0,y_range=Range1d(-0.1,1.1),x_range=Range1d(-0.1,10.1))
fig.renderers = [i for i in fig.renderers if 'Glyph' in str(i)]

suptitle = Div(text="<font size=5 color='teal'><b>Save & Load</b></font>")

grid = gridplot([[suptitle],[fig,side_box]],toolbar_location=None)

curdoc().title = 'save & load'
curdoc().add_root(grid)
