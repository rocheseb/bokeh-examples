import os
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Button, CustomJS
from bokeh.layouts import widgetbox

app_path = os.path.dirname(__file__)
datajs = os.path.join(app_path,'templates','data.js')

content = "var DATA = {'a':[5,4,3],'b':{'c':[10,12,14]}};"""

outfile = open(datajs,'w')
outfile.writelines(content)
outfile.close()

button = Button(label='test',width=200)
button.callback = CustomJS(code="custom();")

curdoc().add_root(widgetbox(button))