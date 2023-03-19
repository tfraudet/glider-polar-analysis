from dash import Dash, html, dcc, ctx
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import json

import plotly.graph_objects as go
import plotly.express as px

import numpy as np
import glider.polar as gp

def render_tab_compare_polars(polars_db):
	options = polars_db.findByMethod()
	return html.Div(className='mx-5 mt-3', children = [
		# dcc.Store(id='polars-selection', storage_type='session'),
		# dcc.Store(id='polars-selection', storage_type='memory'),
		dbc.Row( 
			[dbc.Col(className='mt-2', children=[
				html.Div(["Glider #1", dcc.Dropdown( options, id='glider-1',persistence=True, persistence_type='session')])], 
				width=6),
			dbc.Col(className='mt-2', children=[
				html.Div(["Glider #2",dcc.Dropdown(options, id='glider-2',persistence=True, persistence_type='session')])], 
				width=6)],
			),
		dbc.Row( 
			[dbc.Col(className='mt-2', children=[
				html.Div(["Glider #3", dcc.Dropdown(options, id='glider-3',persistence=True, persistence_type='session')])], 
				width=6),
			dbc.Col(className='mt-2', children=[
				html.Div(["Glider #4",dcc.Dropdown(options, id='glider-4',persistence=True, persistence_type='session')])], 
				width=6)],
			),
		dbc.Row( 
			dbc.Col(
				dcc.Graph(className='mt-3',
					id='speed-polar-compare-graph',
					# figure=fig,
				), 
				width=12)
			),
	])

def update_tab_compare_polars(data):
	us_data = json.loads(data)

	polars = []
	for row in us_data['inputs'].values():
		if row is not None:
			name = row[:row.index('/')-1]
			source = row[row.index('/')+2:]
			# print('Look for glider polar [{}] / [{}]'.format(name,source))
			polars.append(
				gp.PolarsDB.get_instance().fromNameAndSource(name,source)
			)

	# Update plotly figure: Add traces depending on gliders selection
	traces=[]
	for polar in polars:
		x_polar = np.linspace(gp.POLAR_CURVE_START_KM,gp.POLAR_CURVE_END_KM,gp.POLAR_CURVE_NBR_SAMPLE)
		y_polar = polar.curve(x_polar)

		tn = '{} (wing loading: {} kg/m2)'.format(polar.source,  polar.wing_loading)
		trace = go.Scatter( x=x_polar, y=y_polar, mode='lines', 
			name = '<b>{}</b><br><i>{}</i><br>'.format(polar.name,tn),
			hovertemplate='<extra></extra>Speed: %{x:.0f}km/h<br>Sink rate: %{y:.2f}m/s', hoverinfo='x+y')
		traces.append(trace)

	# finalize the layout of the graph
	layout = go.Layout(
		title_text='<b>side by side comparison of speed polars</b>',
		height=800,
		yaxis=dict(range=[-4, 1]),
		xaxis=dict(range=[0, 250]),
		template='ggplot2',
	)
	fig = go.Figure(data=traces, layout=layout)

	fig.update_yaxes(zeroline=True, zerolinewidth=1, zerolinecolor='black',  dtick=0.5)
	fig.update_yaxes(title_text='Vz (m/s)', title_font=dict(size=14, family='Courier', color='crimson'))

	fig.update_xaxes(zeroline=True, zerolinewidth=1, zerolinecolor='black')
	fig.update_xaxes(
		title_text='Vitesse ({})'.format(( 'm/s' if gp.CONVERT_TO_MS else 'km/h')),
		title_font=dict(size=14, family='Courier', color='crimson')
	)
	# fig.update_layout(transition_duration=500, transition_easing= 'elastic-in')

	return fig