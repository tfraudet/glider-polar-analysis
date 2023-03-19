# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, ctx
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import plotly.graph_objects as go
import plotly.express as px

import numpy as np
import glider.polar as gp


from ui.polar_compare import *
from ui.wl_effect import *

URL_ACPH = 'https://aeroclub-issoire.fr'
URL_LOGO_IMG = 'assets/logo-v2017-gray-SD.png'

# load data
polars_db = gp.PolarsDB.get_instance('./glider-polars-db.json')
aGliderPolar = polars_db.fromNameAndSource('LAK19-18m','Manual')

# https://dash-bootstrap-components.opensource.faculty.ai/
app = Dash(__name__,
		external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
		title = 'Glider Porlar Analysis', 
		meta_tags=[
				{"name": "viewport", "content": "width=device-width, initial-scale=1"},
			],
		)
app.config["suppress_callback_exceptions"] = True

@app.callback(
	Output(component_id='wing-loading-output', component_property='children'),
	Output(component_id='wing-loading-slider',component_property='value'),
	Output('speed-polar-graph','figure'),
	Input(component_id='glider-selected', component_property='value'),
	Input(component_id='wing-loading-slider', component_property='value'),
	State('polars-selection', 'data')
)
def callback_update_tab_wingloading_analysis(glider_name, wingloading, data):
	return update_tab_wingloading_analysis(glider_name, wingloading)

@app.callback(
	Output('speed-polar-compare-graph', 'figure'),
	Input('polars-selection', 'data'),
)
def callback_update_tab_compare_polars(data):
	return update_tab_compare_polars(data)

@app.callback(
	Output('polars-selection', 'data'),
	Input(component_id='glider-1', component_property='value'),
	Input(component_id='glider-2', component_property='value'),
	Input(component_id='glider-3', component_property='value'),
	Input(component_id='glider-4', component_property='value'),
)
def callback_polars_selection(g1, g2, g3, g4):
	if ctx.triggered_id is None:
		raise PreventUpdate

	ctx_msg = json.dumps({
		'states': ctx.states,
		'triggered': ctx.triggered,
		'inputs': ctx.inputs
	}, indent=2)

	return ctx_msg

@app.callback(
	Output('tabs-content', 'children'),
	Input('tabs-graph', 'value'),
	State('polars-selection', 'data')
)
def render_tabs_content(active_tab, data):
	if active_tab == 'tab-1-graph':
		return render_tab_wingloading_analysis()
	elif active_tab == 'tab-2-graph':
		return render_tab_compare_polars(polars_db)

header = html.Div(className='mb-5', style={'background-color': 'rgba(0,0,0,.03)', 'color': '#6c757d', 'border': '1px solid rgba(0,0,0,.125)'}, children=[
	dbc.Row( className='py-3', children=[
		dbc.Col(className='', children=[
				html.A(href=URL_ACPH, children=[html.Img(src=URL_LOGO_IMG, className='mx-auto d-block', width=100)]),
			], width=2),
		dbc.Col(className='d-flex align-items-center', children=[
			html.H2('Glider Polar Analysis', style={'color': '#6c757d'})], 
			width=10)],
		),
])

footer = html.Div(className='', style={'background-color': 'rgba(0,0,0,.03)', 'color': '#6c757d', 'border': '1px solid rgba(0,0,0,.125)'}, children=[
	dbc.Row(className='py-2 px-5', children=[
		dbc.Col(className='d-flex justify-content-center align-items-center', children=[
			'Made with',
			html.I(className='fa-solid fa-heart mx-2', style={'color': '#e96656'}),
			html.Span('by'),
			html.A(className='mx-1', href=URL_ACPH, children=['Aéroclub Pierre Herbaud']),
			'-',
			html.I(className='fa-solid fa-bug mx-2', style={'color': '#34d293'}),
			html.A(href='mailto:webmaster@aeroclub-issoire.fr', children=['report a bug']),
		], width=12),
	]),
])

app.layout = html.Div(className='', children=[
	header,
	dcc.Tabs(id="tabs-graph", value='tab-1-graph', className='mx-5', persistence=True, persistence_type='session', children=[
		dcc.Tab(label='Effect of wing loading ', value='tab-1-graph'),
		dcc.Tab(label='Compare polars', value='tab-2-graph'),
	]),
	html.Div(id='tabs-content'),
	footer,
	dcc.Store(id='polars-selection', storage_type='memory'),
])

# https://pythonprogramming.net/deploy-vps-dash-data-visualization/
server = app.server

if __name__ == '__main__':
	app.run(debug=False)
