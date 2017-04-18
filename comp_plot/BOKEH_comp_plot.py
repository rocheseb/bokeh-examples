#!/usr/bin/env python2.7
 # -*- coding: ascii -*-

###########################################################
# 					Sebastien Roche
#			sebastien.roche@mail.utoronto.ca
#     functions to create comparison plots for time series
###########################################################

#######################
# Library description #
#######################

'''
This is an attempt to make a generic function to produce analysis plots for time series.

The function bok_comp(DATA,select,xlab='',ylab='',sup_title='',notes='',prec='2') returns a bokeh gridplot object:

If you have data 'select' to which you want to compare several datasets 'lab0', 'lab1', etc.
the DICTIONARY (or OrderedDict) DATA must be of the form:

DATA={ 
		'lab': {
				'lab0':{x':[...],'y':[...]},
				'select0':{x':[...],'y':[...]},
				'color':'red',
				},
		'lab1': {
				'lab1':{x':[...],'y':[...]},
				'select1':{x':[...],'y':[...]},
				'color':'blue',
				},
		'lab2': {
				'lab2':{x':[...],'y':[...]},
				'select2':{x':[...],'y':[...]},
				'color':'orange',
				},
		etc...
	 }

where 'select0', 'select1' etc are subsets of 'select' containing only data respectively coincident with 'lab0','lab1' etc.

There will be two figures, one table, and one "notes" text widget.
The main figure will show all the time series of coincident data between each 'lab' and 'select'.
The second figure will show a correlation plot including only data selected within the BoxSelect tool.
The data in the table will also be updated based on the data selected within the BoxSelect tool.

	- 'select' is the name of the common data to which all dataset will be compared
	- 'xlab' is the label of the x axis
	- 'ylab' is the label of the y axis
	- 'sup_title' is the hader of the html page
	- 'notes' is a string of html code that will be displayed in a text widget beside the plots
	- 'prec' is a "number string" that sets the precision of the values displayed in the table

the function write_html(bok_obj,tab='bokeh',save='default.html') will create the html plot:
	- "save" is the full path to the html file
	- "tab" is the string that will appear in the browser tab when oppening the html file
	- bok_obj is any bokeh object (figure,gridplot,tabs etc.)
'''

#############
# Libraries #
#############

# general
import os
import sys

# time handling
import time
from datetime import datetime,timedelta

# special arrays with special functions
import numpy as np

# round up
from math import ceil

# interactive plots
from bokeh.plotting import figure
from bokeh.models import Legend, CustomJS, ColumnDataSource, CheckboxGroup, Button, Div, HoverTool
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.layouts import gridplot, widgetbox
from bokeh.resources import CDN
from bokeh.embed import file_html

#############
# Functions #
#############

# make a plot to compare n arrays 
def bok_comp(DATA,select,xlab='',ylab='',sup_title='',notes='',prec='2'):
	"""
	If you have data 'select' to which you want to compare several datasets 'lab0', 'lab1', etc.
	the DICTIONARY (or OrderedDict) DATA must be of the form:

	DATA={ 
			'lab': {
					'lab0':{x':[...],'y':[...]},
					'select0':{x':[...],'y':[...]},
					'color':'red',
					},
			'lab1': {
					'lab1':{x':[...],'y':[...]},
					'select1':{x':[...],'y':[...]},
					'color':'blue',
					},
			'lab2': {
					'lab2':{x':[...],'y':[...]},
					'select2':{x':[...],'y':[...]},
					'color':'orange',
					},
			etc...
		 }

	where 'select0', 'select1' etc are subsets of 'select' containing only data respectively coincident with 'lab0','lab1' etc.

	There will be two figures, one table, and one "notes" text widget.
	The main figure will show all the time series of coincident data between each 'lab' and 'select'.
	The second figure will show a correlation plot including only data selected within the BoxSelect tool.
	The data in the table will also be updated based on the data selected within the BoxSelect tool.

		- 'select' is the name of the common data to which all dataset will be compared
		- 'xlab' is the label of the x axis
		- 'ylab' is the label of the y axis
		- 'sup_title' is the hader of the html page
		- 'notes' is a string of html code that will be displayed in a text widget beside the plots
		- 'prec' is a "number string" that sets the precision of the values displayed in the table
	"""

	######## /!\ important time handling to make sure times don't get shifted from UTC due to computer environment variables when using datetime objects ###########
	os.environ['TZ'] = 'UTC'
	time.tzset()
	# This will not change your system timezone settings
	################################################################################################################################################################

	if sup_title == '':
		sup_title = """<font size="4">Use the "Box Select" tool to select data of interest.</br>The table shows statistics between each dataset and the data shown in black.</font></br></br>"""

	header = Div(text=sup_title,width=700) # the title of the dashboard

	# list of columns for the table
	columns = [ 
				TableColumn(field='Name',title='Name'),
				TableColumn(field='N',title='N'),
				TableColumn(field='RMS',title='RMS'),
				TableColumn(field='Bias',title='Bias'),
				TableColumn(field='Scatter',title='Scatter'),
				TableColumn(field='R',title='R'),
				]

	temp = [0 for i in DATA] # dummy list to initially fill teh columns of the table with zeros

	table_source = ColumnDataSource( data = {'Name':DATA.keys(),'N':temp,'RMS':temp,'Bias':temp,'Scatter':temp,'R':temp} ) # the data source of the table
	
	data_table = DataTable(source=table_source, columns=columns, width= 450, height=45*len(DATA.keys())) # the table itself

	txt = Div(text='Display the table with increasing # before starting a new selection',width = 450) # text div that will be updated with the selected range of date within the BoxSelect tool

	sources = {} # data sources for the main figure
	cor_sources = {} # data sources for the correlation figure
	count = 0 # iterated in the for loop below and used in the sources callbacks
	for label in DATA:
		sources[label] = {} # for each source 'label', there will be two time series, the 'label' data, and the coincident 'select' data
		sources[label][label] = ColumnDataSource(data=DATA[label][label]) # 'label' data
		sources[label][select] = ColumnDataSource(data=DATA[label][select]) # 'select' data that is coincident with 'label' data

		cor_sources[label] = ColumnDataSource(data={'x':[],'y':[]}) # fillable source for the correlation figure

		# give a callback to all 'label' data sources to update the correlation plot and the table based on the BoxSelect tool selection.
		sources[label][label].callback = CustomJS(args = dict(s2=sources[label][select],dt=data_table,scor=cor_sources[label]), code="""
		var inds = cb_obj.selected['1d'].indices;
		var d1 = cb_obj.data;
		var d2 = s2.data;
		var tab = dt.source.data;
		var dcor = scor.data;

		var difm = 0;
		var difm2 = 0;
		var scat = 0;

		var ym1 = 0;
		var ym2 = 0;

		var T1 = 0;
		var T2 = 0;
		var T3 = 0;

		dcor['x'] = [];
		dcor['y'] = [];

		tab['N']["""+str(count)+"""] = inds.length;


		if (inds.length == 0) {
			tab['RMS']["""+str(count)+"""] = 0;
			tab['Bias']["""+str(count)+"""] = 0;
			tab['Scatter']["""+str(count)+"""] = 0;
			tab['R']["""+str(count)+"""] = 0;
			dt.trigger('change');
			return;
		}

		for (i=0; i < inds.length; i++){
			difm += d1['y'][inds[i]] - d2['y'][inds[i]];
			difm2 += Math.pow(d1['y'][inds[i]] - d2['y'][inds[i]],2);
			ym1 += d1['y'][inds[i]];
			ym2 += d2['y'][inds[i]];

			dcor['x'].push(d2['y'][inds[i]]);
			dcor['y'].push(d1['y'][inds[i]]);
		}

		difm /= inds.length;
		difm2 /= inds.length;
		ym1 /= inds.length;
		ym2 /= inds.length;

		for (i=0; i < inds.length; i++){
			scat += Math.pow(d1['y'][inds[i]] - d2['y'][inds[i]] - difm,2);
		}

		for (i=0; i < inds.length; i++){
			T1 += (d1['y'][inds[i]] - ym1)*(d2['y'][inds[i]] - ym2);
			T2 += Math.pow(d1['y'][inds[i]] - ym1,2);
			T3 += Math.pow(d2['y'][inds[i]] - ym2,2);
		}

		tab['RMS']["""+str(count)+"""] = Math.sqrt(difm2).toFixed("""+prec+""");
		tab['Bias']["""+str(count)+"""] = difm.toFixed("""+prec+""");
		tab['Scatter']["""+str(count)+"""] = Math.sqrt(scat/(inds.length -1)).toFixed("""+prec+""");
		tab['R']["""+str(count)+"""] = (T1/Math.sqrt(T2*T3)).toFixed("""+prec+""");

		dt.trigger('change');
		scor.trigger('change');
		""")

		count+=1

	#get the min and max of all the data x and y
	min_x = min([DATA[label][label]['x'][0] for label in DATA])
	max_x = max([DATA[label][label]['x'][-1] for label in DATA])

	min_y = min([min(abs(DATA[label][label]['y'])) for label in DATA])
	max_y = max([max(DATA[label][label]['y']) for label in DATA])

	max_ampli = max_y - min_y

	# we will set the y axis range at +/- 10% of the data max amplitude
	min_y = min_y - max_ampli*10/100
	max_y = max_y + max_ampli*10/100

	TOOLS = ["pan,hover,wheel_zoom,box_zoom,undo,redo,reset,box_select,save"] # interactive tools available in the html plot

	fig = figure(plot_width=900,plot_height=200+35*(len(DATA.keys())-2),tools=TOOLS,x_axis_type='datetime', y_range=[min_y,max_y]) # figure with the time series

	fig.tools[-2].dimensions='width' # only allow the box select tool to select data along the X axis (will select all Y data in a given X range)

	UTC_offset = str((datetime(*time.gmtime()[:6])-datetime(*time.localtime()[:6])).seconds) # machine UTC offset, javascript "Date" in the callback seems to offset the time data by the UTC offset

	# make the BoxSelect tool update the 'txt' Div widget with the currently selected range of dates.
	fig.tools[-2].callback = CustomJS(args=dict(txt=txt),code="""
		var sel = cb_data["geometry"];
		
		var startsec = sel["x0"]/1000;
		var start = new Date(0);

		start.setUTCSeconds(startsec)

		var startstring = ("0" + start.getUTCDate()).slice(-2) + "-" + ("0"+(start.getUTCMonth()+1)).slice(-2) + "-" +start.getUTCFullYear() + " " + ("0" + start.getUTCHours()).slice(-2) + ":" + ("0" + start.getUTCMinutes()).slice(-2);

		var finishsec = sel["x1"]/1000;
		var finish = new Date(0);

		finish.setUTCSeconds(finishsec)

		var finishstring = ("0" + finish.getUTCDate()).slice(-2) + "-" + ("0"+(finish.getUTCMonth()+1)).slice(-2) + "-" +finish.getUTCFullYear() + " " + ("0" + finish.getUTCHours()).slice(-2) + ":" + ("0" + finish.getUTCMinutes()).slice(-2);

		txt.text = 'Selection range from '+startstring + ' to ' + finishstring;

		txt.trigger("change"); 
		""")

	# actual time series
	plots = []
	for label in DATA:
		plots.append( fig.scatter(x='x',y='y',color=DATA[label]['color'],alpha=0.5,source=sources[label][label]) )
		plots.append( fig.scatter(x='x',y='y',color='black',alpha=0.5,source=sources[label][select]) )

	# hover tool configuration
	fig.select_one(HoverTool).tooltips = [
	     ('x, y', '@x, @y'),
	]

	N_plots = range(len(plots)) # used in the checkbox callbacks

	# used in the checkbox callbacks, we will trigger both 'label' and coincident 'select' data visibility at the same time
	N_plots2 = range(len(plots)/2) 
	even_plots = [i for i in N_plots if i%2 == 0]

	# setup the legend and axis labels for the main figure
	legend=Legend(items=[(select,[plots[1]])]+[(DATA.keys()[i],[plots[even_plots[i]]]) for i in range(len(DATA.keys()))],location=(0,0))
	fig.add_layout(legend,'right')
	fig.yaxis.axis_label = ylab
	fig.xaxis.axis_label = xlab

	# correlation figure
	cor_fig = figure(title = 'Correlations', plot_width = 250, plot_height = 280, x_range = [min_y,max_y], y_range = [min_y,max_y]) 
	cor_fig.toolbar.logo = None
	cor_fig.toolbar_location = None
	cor_fig.xaxis.axis_label = ' '.join([select,ylab])
	cor_fig.yaxis.axis_label = ylab

	# one to one line in the correlation plot
	linerange = list(np.arange(0,int(max_y),ceil(max_y)/10.0))+[max_y]
	cor_fig.line(x=linerange,y=linerange,color='black')
	# actual correlation plots
	corplots = []
	for label in DATA:
		corplots.append( cor_fig.scatter(x='x',y='y',color=DATA[label]['color'],alpha=0.5,source=cor_sources[label]) )

	N_corplots = range(len(corplots)) # used in the checkbox callbacks

	checkbox = CheckboxGroup(labels=DATA.keys(),active=range(len(DATA.keys())),width=100) # the group of checkboxes, one for each 'label' in DATA

	iterable = [('p'+str(i),plots[i]) for i in N_plots]+[('pcor'+str(i),corplots[i]) for i in N_corplots]+[('checkbox',checkbox)] # associate each element needed in the callback to a string

	# checkboxes to trigger line visibility
	checkbox_code = """var indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };"""
	checkbox_code += ''.join(['p'+str(i)+'.visible = indexOf.call(checkbox.active, '+str(i/2)+') >= 0; p'+str(i+1)+'.visible= indexOf.call(checkbox.active, '+str(i/2)+') >= 0; pcor'+str(i/2)+'.visible = indexOf.call(checkbox.active, '+str(i/2)+') >= 0;' for i in range(0,len(N_plots),2)])
	checkbox.callback = CustomJS(args={key: value for key,value in iterable}, code=checkbox_code)

	# button to uncheck all checkboxes
	clear_button = Button(label='Clear all',width=100)
	clear_button_code = """checkbox.set("active",[]);"""+checkbox_code
	clear_button.callback = CustomJS(args={key: value for key,value in iterable}, code=clear_button_code)

	# button to check all checkboxes
	check_button = Button(label='Check all',width=100)
	check_button_code = """checkbox.set("active","""+str(N_plots2)+""");"""+checkbox_code
	check_button.callback = CustomJS(args={key: value for key,value in iterable}, code=check_button_code)

	# button to save the table data in a .csv file
	download_button = Button(label='Save Table to CSV',width=100)
	download_button.callback = CustomJS(args=dict(dt=data_table),code="""
	var tab = dt.source.data;
	var filetext = 'Name,N,RMS,Bias,Scatter,R'+String.fromCharCode(10);
	for (i=0; i < tab['Name'].length; i++) {
	    var currRow = [tab['Name'][i].toString(),
	                   tab['N'][i].toString(),
	                   tab['RMS'][i].toString(),
	                   tab['Bias'][i].toString(),
	                   tab['Scatter'][i].toString(),
	                   tab['R'][i].toString()+String.fromCharCode(10)];

	    var joined = currRow.join();
	    filetext = filetext.concat(joined);
	}

	var filename = 'data_result.csv';
	var blob = new Blob([filetext], { type: 'text/csv;charset=utf-8;' });

    var link = document.createElement("a");
    link = document.createElement('a')
    link.href = URL.createObjectURL(blob);
    link.download = filename
    link.target = "_blank";
    link.style.visibility = 'hidden';
    link.dispatchEvent(new MouseEvent('click'))

	""")

	# default text of the 'info' Div widget
	if notes == '':
		notes =   """
				<font size="5"><b>Notes:</b></font></br></br>
				<font size="2">
				Use the "Box Select" tool to select data of interest.</br>
				The table shows statistics between each dataset and the data shown in black.
				</font>
				"""
	dumdiv = Div(text='',width=50) # dummy div widget to force a padding between gridplot elements

	info = Div(text=notes,width=400,height=300) # the information Div widget

	group = widgetbox(checkbox,clear_button,check_button) # group the checkboxes and buttons in a common "widget box"

	table_grid = gridplot([[txt],[download_button],[data_table]],toolbar_location=None) # group together the table, txt Div widget, and download button

	sub_grid = gridplot([[fig,group],[cor_fig,table_grid,dumdiv,info]],toolbar_location='left') # put everything in a grid

	grid = gridplot([[header],[sub_grid]],toolbar_location=None) # put the previous grid under the 'header' Div widget, this is done so that the toolbar of sub_grid won't appear on the side of the header.

	return grid


def write_html(bok_obj,tab='bokeh',save='default.html'):
	"""
	write a html bokeh plot:
		- "save" is the full path to the html file
		- "tab" is the string that will appear in the browser tab when oppening the html file
		- bok_obj is any bokeh object (figure,gridplot,tabs etc.)
	"""
	outfile=open(save,'w')
	outfile.write(file_html(bok_obj,CDN,tab))
	outfile.close()
