####################
# code description #
####################

#############
# Libraries #
#############

import numpy as np

import bokeh
from bokeh.plotting import figure
from bokeh.models import Legend, CustomJS, ColumnDataSource, HoverTool, CheckboxGroup, Button, Div
from bokeh.layouts import gridplot,widgetbox
from bokeh.resources import CDN
from bokeh.embed import file_html

import collections

#############
# Functions #
#############

def descend_values(dic):
	'''
	gets all the values in a dictionnary and put them in a 1d list
	'''
	for key in dic.keys():
		if type(dic[key]) in [dict,collections.OrderedDict]:
			for x in descend_values(dic[key]):
				yield x
		else:
			yield dic[key]

def flatten(obj,keep=[]):
	'''
	gets all the items in a nested iterable oject and put them in a 1d list
	keep is a list of object types that should not be flattened ( in python 3 strings will be "exploded" if str is not in the keep list)
	'''
	if (type(obj) in [dict,collections.OrderedDict]) and ((dict not in keep) and (collections.OrderedDict not in keep)):
		obj = descend_values(obj)

	for item in obj:
		if hasattr(item,'__iter__') and (type(item) not in keep):
			for x in flatten(item,keep=keep):
				yield x
		else:
			yield item

def dumfig(width=600,height=600,legend={}):
	'''
	Need to make a dummy figure to get the legend somewhere by itself ....

	legend is a dict/ordereddict with strcuture:
		- {'name':'color'}
	or  - {'name':{'legend':'name','line_dash':'...','color':'...'}}
	or  - {'name':{'legend':'name','marker':'...','color':'...'}}
	'''
	dumx=range(10)
	dumfig=figure(outline_line_alpha=0,plot_height=height,plot_width=width)
	for key in legend:
		if type(legend[key]) in [dict,collections.OrderedDict]:
			try:
				dumfig.line(x=dumx,y=dumx,visible=False,color=legend[key]['color'],line_width=2,line_dash=legend[key]['line_dash'],legend=legend[key]['legend'])
			except KeyError:
				dumfig.scatter(x=dumx,y=dumx,visible=False,color=legend[key]['color'],marker=legend[key]['marker'],legend=legend[key]['legend'])
		else:
			dumfig.line(x=dumx,y=dumx,visible=False,color=legend[key],line_width=2,legend=key)
	dumfig.renderers=[rend for rend in dumfig.renderers if (type(rend)==bokeh.models.renderers.GlyphRenderer or type(rend)==bokeh.models.annotations.Legend)]
	dumfig.renderers[0].border_line_alpha=0
	dumfig.renderers[0].spacing=6
	dumfig.renderers[0].location='top_left'
	for rend in dumfig.renderers:
		if type(rend)==bokeh.models.renderers.GlyphRenderer:
			rend.visible = False

	return dumfig

def show_hide_button(in_lab,checkbox_name,checkbox_code,iterable,width=100):
	'''
	Button to trigger specific checkboxes in a checkboxgroup if they contain the string 'in_lab'

	Input:
		- name : string of character contained in labels of checkboxes to be checked
		- checkbox_name : the variable name of your checkbox group
		- checkbox_code : the callback code of your checkbox group ( thus the code of the checkbox group should NOT use cb_obj )
		- iterable : list of (key,value) tuples for the arguments of the button callback, the checkbox group must be one of them
	Output:
		- button that check/uncheck checkboxes with 'in_lab' in their label
	'''

	button = Button(label='Hide %s' % in_lab,width = width,button_type='danger',name=in_lab) # button to check/uncheck all boxes with 'prof'

	button_success_code = """new_active = %s.active.slice(); for (i=0;i<%s.labels.length;i++) {if (%s.labels[i].includes('%s') && !(new_active.includes(i))) {new_active.push(i)}};new_active.sort();%s.active = new_active.slice();""" % (checkbox_name,checkbox_name,checkbox_name,in_lab,checkbox_name) + checkbox_code

	button_danger_code = """new_active = %s.active.slice(); for (i=0;i<%s.labels.length;i++) {if (%s.labels[i].includes('%s') && %s.active.includes(i)) {new_active.splice(new_active.indexOf(i),1)}};%s.active = new_active.slice();""" % (checkbox_name,checkbox_name,checkbox_name,in_lab,checkbox_name,checkbox_name) + checkbox_code

	button_code = """if (cb_obj.button_type.includes("danger")){""" \
				+ button_danger_code\
				+ """cb_obj.button_type = "success";cb_obj.label = "Show %s";} else {""" % in_lab \
				+ button_success_code \
				+ """cb_obj.button_type = "danger";cb_obj.label = "Hide %s";}"""  % in_lab

	button.callback = CustomJS(args={key: value for key,value in iterable}, code=button_code)

	return button

def show_hide_button_aware(keyword_dict,checkbox_code,iterable,width=100,separator='-'):
	"""
	Return a number of button that check / uncheck boxes in a CheckBoxGroup based on a keyword list and the CheckBoxGroup labels
	- keyword_dict: an OrderedDict of groups of keywords, each group has keyword of a specific length {key1:['abc','def','ghi',...],key2:['ab','cd',...],...}
	- checkbox_code: callback code of the CheckBoxGroup
	- iterable: list of (key,value) tuples for the arguments of the CheckBoxGroup callback, must include the CheckBoxGroup itself as ('checkbox',CheckBoxGroup)
	- width: width of the buttons

	Output:
		- buttons that check/uncheck checkboxes in a CheckBoxGroup if they include a certain keyword in their label
		- button to uncheck all the checkboxes and switch all buttons to "show"
		- button to check all the checkboxes and switch all buttons to "hide"
	"""

	# create a button for each keyword in keyword_dict
	button_list = []
	for keyword in list(flatten(keyword_dict)):
		button_list.append( Button(label='Hide '+keyword,name=keyword,button_type='danger',width=width) )

	clear_button = Button(label='Clear all',width=width) # button to uncheck all checkboxes
	check_button = Button(label='Check all',width=width) # button to check all checkboxes

	# adds the buttons to the iterable list for the callback arguments
	new_iterable = iterable + [('button_'+button.name,button) for button in button_list]

	# a string of the form '[button_a,button_b,...]' for the callback codes 
	button_str = str(['button_'+button.name for button in button_list]).replace("'","")


	button_key_code = "" # code that goes over each keyword group and button status to reconstruct the label of checkboxes to be checked / unchecked
	show_full_code = "show_full = [];" # the array of labels with associated checkboxes that need to be checked
	show_full = []
	it = 0
	loopid = ['i','j','k','l','m','n','o','p','q','r','s','t']
	for key in keyword_dict: # loop to generate the code based on the number of keyword groups
		button_key_code += '''
		show_%s = [];
		for (i=0;i<show_name.length;i++){
		if(show_name[i].length==%s){show_%s.push(show_name[i])};
		};
		''' % (key,str(len(keyword_dict[key][0])),key)

		show_full_code += "for(%s=0;%s<show_%s.length;%s++){" % (loopid[it],loopid[it],key,loopid[it])

		show_full.append( 'show_%s[%s]' % (key,loopid[it]) )

		it+=1 

	show_full_code += "show_full.push("+("+'"+separator+"'+").join(show_full)+")"+"};"*it

	button_key_code += show_full_code

	# initial code for the buttons
	button_switch_code = """
	if (cb_obj.button_type.includes("danger")){
		cb_obj.button_type = "success";
		cb_obj.label = "Show "+cb_obj.name;
	} else {
		cb_obj.button_type = "danger";
		cb_obj.label = "Hide "+cb_obj.name;
	}

	button_list = """+button_str+""";
	"""	

	# initial code for the "clear all" button
	clear_switch_code = """
	button_list = """+button_str+""";

	for (i=0;i<button_list.length;i++){
		button_list[i].button_type = "success"
	}
	"""

	# initial code for the "check all" button
	check_switch_code = """
	button_list = """+button_str+""";

	for (i=0;i<button_list.length;i++){
		button_list[i].button_type = "danger"
	}
	"""

	button_code = button_switch_code+"""
	show_name = [];

	for(i=0;i<button_list.length;i++) {
		if(button_list[i].button_type.includes("danger")) {show_name.push(button_list[i].name)};
	};

	"""+button_key_code+"""

	new_active = [];

	for (i=0;i<show_full.length;i++){
		for(j=0;j<checkbox.labels.length;j++){
		if (checkbox.labels[j].includes(show_full[i])) {new_active.push(j);};
		};
	};
	new_active.sort();
	checkbox.active = new_active.slice();

	"""+checkbox_code

	for button in button_list:
		button.callback = CustomJS(args={key:value for key,value in new_iterable}, code=button_code)

	clear_button_code = button_code.replace(button_switch_code,clear_switch_code)
	clear_button.callback = CustomJS(args={key: value for key,value in new_iterable}, code=clear_button_code)

	check_button_code = button_code.replace(button_switch_code,check_switch_code)
	check_button.callback = CustomJS(args={key: value for key,value in new_iterable}, code=check_button_code)

	return [clear_button,check_button]+button_list

###########
# Example #
###########

if __name__ == "__main__":

	# load sample data
	asza = np.load('sza.npy',encoding='latin1').item()
	column = np.load('column.npy',encoding='latin1').item()

	color_dict = {'6220':'green','6339':'pink','6073':'red','4852':'orange'}

	TOOLS="box_zoom,wheel_zoom,pan,undo,redo,reset,hover,save"

	fig = figure(tools=TOOLS)

	for date in column:
		for window in column[date]:
			for mod in column[date][window]:
				source = ColumnDataSource(data={'x':np.array([asza[date][window][spec_ID] for spec_ID in asza[date][window]]),'y':np.array([column[date][window][mod][spec_ID] for spec_ID in column[date][window][mod]]),'specID':[i for i in column[date][window][mod]],'date':['-'.join([date[:4],date[4:6],date[6:8]]) for i in column[date][window][mod]] })
				if mod=='scl':
					fig.scatter(x='x',y='y',color=color_dict[window],marker="triangle",name='-'.join([date,window,mod]),source=source)
				else:
					fig.scatter(x='x',y='y',color=color_dict[window],name='-'.join([date,window,mod]),source=source)

	fig.select_one(HoverTool).tooltips = [
		('date','@date'),
		('spectrum #', '@specID'),
	    ('SZA','@x'),
	]

	fig.xaxis.axis_label = 'SZA (degrees)'
	fig.yaxis.axis_label = 'CO2 column (molecules / cm^2)'

	# setup the dummy figure for the legend
	dumleg = collections.OrderedDict( 
										[('prf',{'legend':'profile','marker':'circle','color':'black'}),('scl',{'legend':'scaling','marker':'triangle','color':'black'})]\
										+[(window,color_dict[window]) for window in column[date]]
										)

	dumfig = dumfig(height=250,width=100,legend=dumleg)

	# CheckboxGroup
	rend_list = [rend for rend in fig.renderers if type(rend)==bokeh.models.renderers.GlyphRenderer]
	checkbox = CheckboxGroup(labels=[rend.name for rend in rend_list],active=list(range(len(rend_list))),height=400)

	# each scatter glyph is associated with a name, the CheckboxGroup too
	iterable = [('p'+str(rend_list.index(rend)),rend) for rend in rend_list]+[('checkbox',checkbox)]

	# code to trigger glyph visibility with checkboxes
	checkbox_code = ''.join(['p'+str(rend_list.index(rend))+'.visible=checkbox.active.includes('+str(rend_list.index(rend))+');' for rend in rend_list])

	# CheckboxGroup callback
	checkbox.callback = CustomJS(args={key:value for key,value in iterable}, code=checkbox_code)

	# Dictionary of keyword groups for the button generating function
	keyword_dict = collections.OrderedDict([('date',sorted(column.keys())),('window',sorted(column[date].keys())),('ret',sorted(column[date][window].keys()))])

	# create all the buttons
	button_list = show_hide_button_aware(keyword_dict,checkbox_code,iterable,width=120)

	# first two buttons are "clear all" and "check all" buttons
	clear_button,check_button = button_list[:2]
	button_list = button_list[2:]

	# insert a text between each group of buttons
	widget_list = [Div(text='Dates (yyyymmdd):',width=120)]
	it=0
	for date in column:
		widget_list.append(button_list[it])
		it+=1
	widget_list.append(Div(text='Windows:',width=120))
	for window in column[date]:
		widget_list.append(button_list[it])
		it+=1
	widget_list.append(Div(text='Retrieval:',width=120))
	for mod in column[date][window]:
		widget_list.append(button_list[it])
		it+=1

	notes = """
	<font size='4'><b>Notes:</b></font><br>
	<br>
	<font size='2'>
	Insert notes here</br>
	</font>
	"""

	txt = Div(text=notes,width=300)

	group = widgetbox(children=widget_list,width=130) 
	group_2 = widgetbox(txt,clear_button,check_button,checkbox,width=350)

	grid=gridplot([[fig,dumfig,group,group_2]],toolbar_location='left')

	outfile=open('col_vs_sza.html','w')
	outfile.write(file_html(grid,CDN,'column'))
	outfile.close()