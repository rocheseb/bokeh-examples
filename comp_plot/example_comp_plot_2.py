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

import sys

# special arrays with special functions
import numpy as np

# generic functions to build a html dashboard to compare time series.
from BOKEH_comp_plot import *

import netCDF4

#############
# Main code #
#############

# those two lines would generate a FREQ_DATA dictionary that would do daily matching and averaging of all sites with the 'Lamont' site
#DATA = np.load('TCCON_sample_data_xco2.npy').item()
#FREQ_DATA = freq_match(DATA,'Lamont','1 days',date_range=['2015-01-01','2016-01-01'],save='TCCON_sample_data_co2_freq_1_days.npy')


FREQ_DATA = np.load('TCCON_sample_data_co2_freq_1_days.npy').item() # this data was generated with the freq_match() function, using full time series of xCO2 from all TCCON sites (I didn't include that as it is ~70 MB)

title = """ 
<div align='right'>
	<img src='TCCON_logo.png' height='50' />
	<font size="6">
		Daily XCO2 over TCCON sites</br>
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
Links: <a href='http://www.tccon.caltech.edu/'>TCCON</a>; 
</font>
"""

write_html(bok_comp(FREQ_DATA, select='Lamont', ylab='XCO2 (ppm)', xlab='Time (UTC)', prec='3', notes=notes, sup_title=title), tab='TCCON_XCO2', save='TCCON_XCO2.html')

