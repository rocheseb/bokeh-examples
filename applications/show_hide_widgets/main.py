from bokeh.io import curdoc
from bokeh.models import Button, Slider, TextInput, Select, CustomJS
from bokeh.layouts import widgetbox,gridplot

start_button = Button(label="Start the experiment") 
stop_button = Button(label="Stop", disabled=True)
m1_text = TextInput(title="mass of puck1 =", value="570")
spark_timer = Slider(value=0, start=0, end=100, step=1, title="Title")

button_map = {
    "Start_Button": start_button,
    "Stop_Button": stop_button, 
    "Mass_of_m1": m1_text,
    "Spark": spark_timer
}
button_call = Select(title="Button call", options=sorted(button_map.keys()), 
value="Start_Button")

select_code = """
to_show = cb_obj.value;
options = cb_obj.options

for (i=0;i<options.length;i++) {
	document.getElementsByClassName(options[i])[0].style.display = "None";
}

document.getElementsByClassName(to_show)[0].style.display = "";
"""

button_call.callback = CustomJS(code=select_code)

box_1 = widgetbox(start_button,css_classes = ['Start_Button'])
box_2 = widgetbox(stop_button,css_classes = ['Stop_Button'])
box_3 = widgetbox(m1_text,css_classes = ['Mass_of_m1'])
box_4 = widgetbox(spark_timer,css_classes = ['Spark'])


grid = gridplot([[button_call],[box_1,box_2,box_3,box_4]],toolbar_location=None)

curdoc().add_root(grid)