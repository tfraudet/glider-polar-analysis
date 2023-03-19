from dash import Dash, html, dcc, ctx
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash
import json

import plotly.graph_objects as go
import plotly.express as px

import numpy as np
import glider.polar as gp

def polar_to_string(p):
	polar_str = '{}x<sup>2</sup>'.format(round(p.coeffs[0],4))
	polar_str += (' + ' if (p.coeffs[1] >= 0 ) else ' ')
	polar_str += '{}x'.format(round(p.coeffs[1],4))
	polar_str += (' + ' if (p.coeffs[2] >= 0 ) else ' ')
	polar_str += '{}'.format(round(p.coeffs[2],4))
	return polar_str

def render_tab_wingloading_analysis():
	options = gp.PolarsDB.get_instance().findByMethod(['ABC','3-points'])
	return html.Div(className='mx-5', children = [
		dbc.Row(className='my-4', children= [ 
			dbc.Col(
				html.Div([
					dbc.Label("Select a glider polar"),
					dcc.Dropdown(options=options,id='glider-selected',persistence=True, persistence_type='session')
				]), 
				width={"size": 3, "offset": 1}
			),
			dbc.Col(
				html.Div([
					"Wing loading: ",
					html.Span(id='wing-loading-output'),
					dcc.Slider(30, 52, 0.1, id='wing-loading-slider',persistence=True, persistence_type='session',
						marks={30 : '30 kg/m2', 35: '35 kg/m2', 40: '40 kg/m2', 45: '45 kg/m2', 50: '50 kg/m2'} ),
				]),
				width={"size": 5, "offset": 1}
			)]),
		dbc.Row( 
			dbc.Col(
				dcc.Graph(
					id='speed-polar-graph',
					# figure=fig,
				), 
				width=12)
			),
	])

def update_tab_wingloading_analysis(glider_name, wingloading_value):
	if glider_name is None:
		raise PreventUpdate

	name = glider_name[:glider_name.index('/')-1]
	source = glider_name[glider_name.index('/')+2:]
	# print('in update_tab_wingloading_analysis(), name={}, source={}, wing loading={}, triggered_id={}'.format(name,source,wingloading_value,ctx.triggered_id))
	aGliderPolar = gp.PolarsDB.get_instance().fromNameAndSource(name,source)

	# update the polar of the selected glider is we wing loading slider has moved
	if (ctx.triggered_id == 'wing-loading-slider'):
		aGliderPolar.update_wing_loading(wingloading_value)
	else:
		wingloading_value = aGliderPolar.wing_loading

	x_polar = np.linspace(gp.POLAR_CURVE_START_KM,gp.POLAR_CURVE_END_KM,gp.POLAR_CURVE_NBR_SAMPLE)
	y_polar = aGliderPolar.curve(x_polar)
	y_ref_polar = aGliderPolar.init_curve(x_polar)

	# Update plotly figure
	traces=[]
	colors = px.colors.qualitative.Plotly

	# add the reference trace
	trace = go.Scatter( x=x_polar, y=y_ref_polar, mode='lines', 
		name = '<i>Initial<br>(wing loading: {} kg/m2)</i>'.format(aGliderPolar.init_wing_loading),
		line = dict(dash='dash') ,
		hovertemplate='<extra></extra>Speed: %{x:.0f}km/h<br>Sink rate: %{y:.2f}m/s', hoverinfo='x+y', )
	traces.append(trace)

	#TODO: what about ABC method ?
	if isinstance(aGliderPolar, gp.PolarGlider3Points):
		traces.append(go.Scatter( x=aGliderPolar.speed, y=aGliderPolar.sink_rate, mode='markers', name='<i>p1, p2, p3 points</i>', marker_symbol = 'diamond',marker=dict(color=colors[1], size=10),
			text=['Point #1', 'Point #2', 'Point #3'], hovertemplate='<extra></extra><b>%{text}</b><br>Speed: %{x}km/h<br>Sink rate: %{y}m/s', hoverinfo='x+y+text'))

	# add the horizontal tangent to the polar
	tg_x = np.arange(0,250)
	tgh_y, x_int, y_int = aGliderPolar.tangent_horizontal(tg_x)
	tg_trace = go.Scatter( x=tg_x, y=tgh_y, mode='lines', name = 'Horizontal tangent', line = dict(dash='dash') )
	msr_marker = go.Scatter( x=x_int, y=y_int, mode='markers', name = 'Min sink rate', marker_symbol = 'x-dot',marker=dict(color=colors[2], size=10), 
		hovertemplate='<extra></extra>Speed: %{x:.1f}km/h<br>Sink rate: %{y:.2f}m/s', hoverinfo='x+y' )
	traces.append(tg_trace)
	traces.append(msr_marker)

	# add the tangent to the polar crossing origin(0,0)
	tgao_y, x_int, y_int = aGliderPolar.tangent_at_origin(tg_x)
	tg_trace = go.Scatter( x=tg_x, y=tgao_y, mode='lines', name = 'Tangent at (0,0)', line = dict(dash='dash') )
	msr_marker = go.Scatter( x=x_int, y=y_int, mode='markers', name = 'Max glide ratio', marker_symbol = 'circle',marker=dict(color=colors[3], size=10),
			hovertemplate='<extra></extra>Speed: %{x:.1f}km/h<br>Sink rate: %{y:.2f}m/s', hoverinfo='x+y' )
	traces.append(tg_trace)
	traces.append(msr_marker)

	# Then add the curve that will be adjusted base on wing loading
	traces.append(go.Scatter( x=x_polar, y=y_polar, mode='lines+markers', 
		name = '<b>Adjusted Polar</b><br>(wing loading: {} kg/m2)'.format(aGliderPolar.wing_loading),
		hovertemplate='<extra></extra>Speed: %{x:.0f}km/h<br>Sink rate: %{y:.2f}m/s', hoverinfo='x+y', ))

	# finalize the layout of the graph
	layout = go.Layout(
		title_text='<b>{}</b><span class="font-size: smaller;"> (wing area: {}m2 - method {})</span>'.format(aGliderPolar.name,aGliderPolar.wing_area,aGliderPolar.method()),
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
	fig.update_layout(transition_duration=500, transition_easing= 'elastic-in')
	
	# Min sink rate annotation
	min_sink_rate = aGliderPolar.get_min_sink_rate()
	text_annotation = '<b>Min sink rate</b><br> speed: {}km/h<br> Vz: {}m/s<br>L/D: {}'.format(round(min_sink_rate[0],1),round(min_sink_rate[1],2), round(min_sink_rate[2],1) )
	fig.add_annotation(
			name = 'min-sink-rate',
			x=min_sink_rate[0], y=min_sink_rate[1], 
			text=text_annotation,
			bgcolor="white", borderpad=8, bordercolor='gray', borderwidth=2,
			showarrow=True,
			yshift=-5,
			ax= -10, ay= 80,
			arrowhead=2,  arrowsize=1, arrowwidth=2,
		)

	# Max glide ratio annotation
	max_gilde_ratio = aGliderPolar.get_max_glide_ratio()
	text_annotation = '<b>Max glide ratio</b><br> speed: {}km/h<br> Vz: {}m/s<br>L/D: {}'.format(round(max_gilde_ratio[0],1),round(max_gilde_ratio[1],2), round(max_gilde_ratio[2],1) )
	fig.add_annotation(
			name = 'max-glide-ratio',
			x=max_gilde_ratio[0], y=max_gilde_ratio[1], 
			text=text_annotation,
			bgcolor="white", borderpad=8, bordercolor='gray', borderwidth=2,
			showarrow=True,
			yshift=5,xshift=5,
			ax= 100, ay= -50,
			arrowhead=2,  arrowsize=1, arrowwidth=2,
		)
	
	# Speed polar equation
	text_annotation = 'Polynomial equation for the polar:<br> {}'.format( polar_to_string(aGliderPolar.polynomial))
	fig.add_annotation(
			name = 'polynomial',
			x=gp.xaxis_unit(50), y=0.4, 
			text=text_annotation,
			bgcolor="white",
			borderpad=8,
			bordercolor='gray',
			borderwidth=4,
			showarrow=False,
		)

	#Update wing loading output label
	wl_output_label = '{} kg/m2'.format(wingloading_value)

	if (ctx.triggered_id == 'glider-selected'):
		return [wl_output_label, wingloading_value, fig]
	else:
		return [wl_output_label, dash.no_update, fig]
