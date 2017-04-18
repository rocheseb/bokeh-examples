#!/usr/bin/env python
 # -*- coding: ascii -*-

####################
# code description #
####################

"""
compare pressure measurements between different sensors in Eureka
ParoSci 765 was a calibration sensor brought to Eureka during the extensive phase of the 2017 ACE/OSIRIS Validation campaign
Vaisala PTU300 is the pressor sensor we use in parallel to TCCON measurements: 0.15 hPa accuracy
Setra is the pressor sensor we used so far to process Eureka TCCON data: 0.55 hPa accuracy
"""

####################
# import libraries #
####################

# special arrays with special functions
import numpy as np

# generic functions to build a html dashboard to compare time series.
from BOKEH_comp_plot import *

#############
# Main code #
#############

DATA = np.load('pressure_sample_data.npy').item()

title = """ 
<div align='right'>
	<img src='PEARL_logo.jpg' height='100' />
	<font size="6">
		Pressure measurements in Eureka</br>
		</br>
	</font>
</div>
"""

notes = """
<font size="5"><b>Notes:</b></font></br>
</br>
<font size="2">
Use the "Box Select" tool to select data of interest.</br>
The table shows statistics between each dataset and the data shown in black.</br>
</br>
Links: <a href='http://www.bakker-co.com/wp-content/uploads/2012/06/Model765.pdf'>ParoSci 765</a>; 
<a href='http://www.vaisala.com/Vaisala%20Documents/Brochures%20and%20Datasheets/CEN-TIA-G-PTU300-Combined-Brochure-B210954EN-E-LOW-v6.pdf'>Vaisala</a>
</font>
"""

write_html(bok_comp(DATA, select='ParoSci 765', ylab='Pressure (hPa)', xlab='Time (UTC)', prec='3', notes=notes, sup_title=title), tab='euPres', save='prescal.html')
