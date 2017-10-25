from bokeh.io import show
from bokeh.plotting import figure
from bokeh.models import TapTool, HoverTool, ColumnDataSource, CustomJS

source_A = ColumnDataSource(data={'x':range(10),'y':range(10)})
source_B = ColumnDataSource(data={'x':range(10),'y':range(10)[::-1]})

fig = figure(tools='tap')

line_A = fig.line(x='x',y='y',color='lightgrey',line_alpha=0.3,hover_color='red',hover_alpha=1,line_width=3,name='A',source=source_A)
line_B = fig.line(x='x',y='y',color='lightgrey',line_alpha=0.3,hover_color='blue',hover_alpha=1,line_width=3,name='B',source=source_B)

fig.add_tools(HoverTool(renderers=[line_A]))
fig.add_tools(HoverTool(renderers=[line_B]))

code = """
console.log(line.name);
if (line.name==='A') {color='red';} else {color='blue';}

if (line.glyph.line_alpha.value===0.3){
	line.glyph.line_alpha.value=1;
	line.glyph.line_color.value=color;
} else {
	line.glyph.line_alpha.value=0.3;
	line.glyph.line_color.value="lightgrey";
}
cb_obj.selected['0d'] = {'indices':Array(0),'glyph':null,'get_view':cb_obj.selected['0d'].get_view};
"""

source_A.js_on_change('selected',CustomJS(args={'line':line_A},code=code))
source_B.js_on_change('selected',CustomJS(args={'line':line_B},code=code))

show(fig)
