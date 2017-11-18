# -*- coding: utf-8 -*-

import numpy as np
import scipy.special

from bokeh.io import curdoc
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.plotting import figure

params = {
	'normal':{'title':'Normal Distribution (μ=0, σ=0.5)',},

	'log normal':{'title':'Log Normal Distribution (μ=0, σ=0.5)',},

	'gamma':{'title':'Gamma Distribution (k=1, θ=2)',},

	'weibull':{'title':'Weibull Distribution (λ=1, k=1.25)',},
}

def update_hist_fig(attr,old,new):

	try:
		new_id = new['1d']['indices'][0]
	except IndexError:
		return

	select_points = curdoc().select_one({"name":"select_points"})

	selected = select_points.data_source.data['txt'][new_id]

	hist_fig = curdoc().select_one({"name":"hist_fig"})
	hist_fig.title.text = params[selected]['title']

	hist_data = params[selected]['hist_data']
	hist = curdoc().select_one({"name":"hist"})
	hist.data_source.data.update(hist_data)

	lines_data = params[selected]['lines_data']

	pdf_line = curdoc().select_one({"name":"pdf"})
	pdf_line.data_source.data.update(lines_data)

	cdf_line = curdoc().select_one({"name":"cdf"})
	cdf_line.data_source.data.update(lines_data)

hist_fig = figure(title="Normal Distribution (μ=0, σ=0.5)",tools="save",background_fill_color="#E8DDCB",name="hist_fig")

mu, sigma = 0, 0.5

measured = np.random.normal(mu, sigma, 1000)
hist, edges = np.histogram(measured, density=True, bins=50)

x = np.linspace(-2, 2, 1000)
pdf = 1/(sigma * np.sqrt(2*np.pi)) * np.exp(-(x-mu)**2 / (2*sigma**2))
cdf = (1+scipy.special.erf((x-mu)/np.sqrt(2*sigma**2)))/2

params['normal']['hist_data'] = {'top':hist,'left':edges[:-1],'right':edges[1:]}
params['normal']['lines_data'] = {'x':x,'pdf':pdf,'cdf':cdf}

source = ColumnDataSource(data=params['normal']['hist_data'])
hist_fig.quad(top='top', bottom=0, left='left', right='right',fill_color="#036564", line_color="#033649",name='hist',source=source)

source = ColumnDataSource(data=params['normal']['lines_data'])
hist_fig.line(x='x', y='pdf', line_color="#D95B43", line_width=8, alpha=0.7, legend="PDF",source=source,name='pdf')
hist_fig.line(x='x', y='cdf', line_color="white", line_width=2, alpha=0.7, legend="CDF",source=source,name='cdf')

hist_fig.legend.location = "center_right"
hist_fig.legend.background_fill_color = "darkgrey"
hist_fig.xaxis.axis_label = 'x'
hist_fig.yaxis.axis_label = 'Pr(x)'

mu, sigma = 0, 0.5

measured = np.random.lognormal(mu, sigma, 1000)
hist, edges = np.histogram(measured, density=True, bins=50)

x = np.linspace(0.0001, 8.0, 1000)
pdf = 1/(x* sigma * np.sqrt(2*np.pi)) * np.exp(-(np.log(x)-mu)**2 / (2*sigma**2))
cdf = (1+scipy.special.erf((np.log(x)-mu)/(np.sqrt(2)*sigma)))/2

params['log normal']['hist_data'] = {'top':hist,'left':edges[:-1],'right':edges[1:]}
params['log normal']['lines_data'] = {'x':x,'pdf':pdf,'cdf':cdf}

k, theta = 1.0, 2.0

measured = np.random.gamma(k, theta, 1000)
hist, edges = np.histogram(measured, density=True, bins=50)

x = np.linspace(0.0001, 20.0, 1000)
pdf = x**(k-1) * np.exp(-x/theta) / (theta**k * scipy.special.gamma(k))
cdf = scipy.special.gammainc(k, x/theta) / scipy.special.gamma(k)

params['gamma']['hist_data'] = {'top':hist,'left':edges[:-1],'right':edges[1:]}
params['gamma']['lines_data'] = {'x':x,'pdf':pdf,'cdf':cdf}

lam, k = 1, 1.25

measured = lam*(-np.log(np.random.uniform(0, 1, 1000)))**(1/k)
hist, edges = np.histogram(measured, density=True, bins=50)

x = np.linspace(0.0001, 8, 1000)
pdf = (k/lam)*(x/lam)**(k-1) * np.exp(-(x/lam)**k)
cdf = 1 - np.exp(-(x/lam)**k)

params['weibull']['hist_data'] = {'top':hist,'left':edges[:-1],'right':edges[1:]}
params['weibull']['lines_data'] = {'x':x,'pdf':pdf,'cdf':cdf}

select_fig = figure(tools='tap',outline_line_alpha=0,min_border_top=20)
select_fig.renderers = []
select_source = ColumnDataSource(data={'x':[1,1,1,1],'y':[0,1,2,3],'txt':['normal','log normal','gamma','weibull'],'color':['red','green','blue','magenta']})
select_fig.scatter(x='x',y='y',color='color',size=20,source=select_source,name='select_points')
labset = LabelSet(x='x',y='y',text='txt',y_offset=-8,x_offset=20,source=select_source)
select_fig.add_layout(labset)

select_source.on_change('selected',update_hist_fig)

curdoc().add_root(gridplot(select_fig,hist_fig, ncols=2, plot_width=400, plot_height=400, toolbar_location=None))