from bokeh.io import curdoc
from bokeh.models import CheckboxButtonGroup

# button group with 3 buttons
group = CheckboxButtonGroup(labels=list('012'),active=[])

# write a function for each button
def stuff_0(in_active):
	if in_active:
		print 'do stuff'
	else:
		print 'undo stuff'
def stuff_1(in_active):
	if in_active:
		print 'yes'
	else:
		print 'no'
def stuff_2(in_active):
	if in_active:
		print 'banana'
	else:
		print 'apple'

# put the functions in a list
stuff_list = [stuff_0,stuff_1,stuff_2]

# on_change callback for the CheckboxButtonGroup, occurs whenever a button is clicked
def do_stuff(attr,old,new):
	print attr,old,new
	'''
	# this loops over all buttons and do stuff with all of them whenever one button is clicked
	for i in [0,1,2]:
		stuff = stuff_list[i]
		in_active = i in new
		stuff(in_active)
	'''

	# this gets the ID of the last clicked button from the change in the 'active' list of the CheckboxButtonGroup
	last_clicked_ID = list(set(old)^set(new))[0] # [0] since there will always be just one different element at a time
	print 'Last button clicked:', group.labels[last_clicked_ID]
	last_clicked_button_stuff = stuff_list[last_clicked_ID]
	in_active = last_clicked_ID in new
	last_clicked_button_stuff(in_active)

# assign the callback to the CheckboxButtonGroup
group.on_change('active',do_stuff)

curdoc().add_root(group)