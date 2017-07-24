import numpy as np
from random import random

from bokeh.io import show
from bokeh.plotting import figure
from bokeh.models import LinearColorMapper, ColorBar, ColumnDataSource, HoverTool, RangeSlider, PreText, CustomJS, Div
from bokeh.layouts import gridplot
from bokeh.resources import CDN
from bokeh.embed import file_html
from bokeh.palettes import Magma256

def flatten(obj):

	for item in obj:
		if hasattr(item,'__iter__'):
			for x in flatten(item):
				yield x
		else:
			yield item

def heatpack(matrix,palette=Magma256,low=None,high=None,low_color='gray',high_color='red',start=None,end=None,step=None,height=600,width=600):
	"""
	input:
		- width / height : width and height of the heatmap figure
		- matrix: 2D array
		- palette: list of colors
		- low: low value of the ColorMapper
		- high: high value of the ColorMapper
		- low_color: values below "low" will have that color
		- high_color: values above "high" will have that color
		- start / end : range for the slider
		- step: step of the range slider

	output:
		- the heatmap figure
		- dummy figure with the colorbar
		- range slider to change the low / high values of the color mapper
	"""

	# make sure the 2D array is a numpy array
	if type(matrix)!=np.ndarray:
		matrix = np.array(matrix) 

	if start == None:
		start = matrix.min()
	if end == None:
		end = matrix.max()
	if step == None:
		step = (end-start)/100

	if low == None:
		low = matrix.min()
	if high == None:
		high = matrix.max()

	mapper = LinearColorMapper(palette=palette, low=low, high=high,low_color=low_color,high_color=high_color) # linearly map the "magma" list to the [low,high] range

	color_bar = ColorBar(color_mapper=mapper,location=(0,0),label_standoff=15) # define the color bar with the linear color mapper

	len_mat = len(matrix)
	IDs = list(range(len_mat))*len_mat # list of column indices for the flattened matrix elements
	source = ColumnDataSource( data={'row':np.array(sorted(IDs)),'col':np.array(IDs),'mat':np.array(list(flatten(matrix)))} )

	TOOLS = "box_zoom,hover,save,pan,reset,wheel_zoom" # interactive tools for the plot

	# the heatmap plot
	fig = figure(plot_width=width,plot_height=height,tools=TOOLS)
	rect = fig.rect(x='col',y='row',width=1,height=1,source=source,fill_color = {'field':'mat','transform':mapper},line_color=None)

	# plot cosmetics
	fig.grid.grid_line_color = None
	fig.axis.axis_line_color = None
	fig.axis.major_tick_line_color = None
	fig.axis.major_label_standoff = 0
	fig.x_range.range_padding = 0 # prevents white bands on the inner sides of the plot
	fig.y_range.range_padding = 0 # prevents white bands on the inner sides of the plot

	# use a dummy figure to add the color bar (because add_layout will compress your plot)
	dumx=range(10)
	dumfig=figure(outline_line_alpha=0,plot_height=height,plot_width=120)
	dumfig.line(x=dumx,y=dumx,visible=False)
	for rend in dumfig.renderers:
		rend.visible = False
	dumfig.add_layout(color_bar,'left')

	# configure the Hover tool
	fig.select_one(HoverTool).tooltips = [
	     ('row, col', '@row, @col'),
	     ('value', '@mat'),
	]

	# widgets
	select = RangeSlider(start=start,end=end,step=step,range=(low,high),callback_policy = 'mouseup')

	# javascript callback codes for the widgets
	select_code = """
	var maxval = select.range[1];
	var minval = select.range[0]

	map.high = maxval;
	map.low = minval;
	"""

	# widget callbacks
	select.callback = CustomJS(args=dict(map=mapper,src=source,select=select), code = select_code)

	return fig,dumfig,select


if __name__ == "__main__":

	# color list to use for the color bar
	magma = Magma256[::-1] 

	# some data to plot
	matrix = np.array([[100*random() for j in range(100)] for i in range(100)])

	fig,dumfig,select = heatpack(matrix,palette=magma,low=10,high=90,start=0,end=100,step=1,width=400,height=400)

	# add some text widgets
	text = PreText(text='The low/high of the color mapper will be set to the values of the range slider\nValues > max are shown in red\nValues < min are shown in gray',width=800)
	head = Div(text='<font size="12">Heatmap</font></b>',width=800)

	# final plot layout
	grid = gridplot([[fig,dumfig]],toolbar_location='left')
	final = gridplot([[head],[select,text],[grid]],toolbar_location=None) # I put the first grid in a second one so I do not havet he final toolbar by the widgets

	# write html file
	outfile=open('heatmap.html','w')
	outfile.write(file_html(final,CDN,'heatmap'))
	outfile.close()