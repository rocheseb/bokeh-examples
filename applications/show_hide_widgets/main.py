from bokeh.io import curdoc
from bokeh.models import Button, Slider, TextInput, Select, CustomJS
from bokeh.layouts import widgetbox,gridplot

start_button = Button(label="Start the experiment") 
stop_button = Button(label="Stop", disabled=True)
m1_text = TextInput(title="mass of puck1 =", value="570")
spark_timer = Slider(value=0, start=0, end=100, step=1, title="Title")

button_list = ["Start_Button","Stop_Button","Mass_of_m1","Spark"]

button_call = Select(title="Button call", options=sorted(button_list), value="Start_Button",width=200)

select_code = """
to_show = cb_obj.value;
options = cb_obj.options

for (i=0;i<options.length;i++) {
	box = document.getElementsByClassName(options[i])[0];
	if (!box.className.includes("hidden")) {box.className+=" hidden";}
	if (box.className.includes(to_show)) {box.className=box.className.replace(" hidden","");}
}
"""

button_call.callback = CustomJS(code=select_code)

box_1 = widgetbox(start_button,css_classes = ['Start_Button'])
box_2 = widgetbox(stop_button,css_classes = ['Stop_Button','hidden'])
box_3 = widgetbox(m1_text,css_classes = ['Mass_of_m1','hidden'])
box_4 = widgetbox(spark_timer,css_classes = ['Spark','hidden'])


grid = gridplot([[button_call],[box_1,box_2,box_3,box_4]],toolbar_location=None)

curdoc().add_root(grid)