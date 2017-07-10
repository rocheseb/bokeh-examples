#!/var/lib/py27_sroche/bin/python
 # -*- coding: ascii -*-

from __future__ import print_function # allows the use of Python 3.x print(function in python 2.x code so that print('a','b') prints 'a b' and not ('a','b')

####################
# code description #
####################

"""
Example of use of the bok_comp function from BOKEH_comp_plot.py to produce a dashboard to compare time series
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


FREQ_DATA = np.load('TCCON_sample_data_co2_freq_1_days.npy').item() # this data was generated with the freq_match() function, using full time series of xCO2 from all TCCON sites (I didn't include that in the repository as it is ~70 MB)

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

