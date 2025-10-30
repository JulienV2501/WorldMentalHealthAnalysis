import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

from data_loader import load_data

from indexMentalHealth import indexMentalHealth
df = load_data(save_as_file = False)
df = indexMentalHealth(df)

illness_cols = [
    'schizo_disorders',
    'depression_disorders',
    'anxiety_disorders',
    'bipolar_disorders',
    'eating_disorders',
    'global_mental_disorders',
    'unemployment_rate',
    'hf_score'
]

illness_labels = {
    illness_cols[0]: 'Schizophrenia disorders',
    illness_cols[1]: 'Depressive Disorders',
    illness_cols[2]: 'Anxiety Disorders',
    illness_cols[3]: 'Bipolar Disorders',
    illness_cols[4]: 'Eating Disorders',
    illness_cols[5]: 'Global Mental Disorders',
    illness_cols[6]: 'Unemployment Rate',
    illness_cols[7]: 'Human Freedom index'
}

min_year = int(df['year'].min())
max_year = int(df['year'].max())

# Default country selection
default_code = None

def code_to_name(code: str) -> str:
    row = df[df['code'] == code].head(1)
    return row['country'].iloc[0] if not row.empty else code

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([

    # ---------------- Title ----------------
    dbc.Row([
        dbc.Col([
            html.H1('Mental Health Disorders by Country', className='text-center mb-4')
        ])
    ]),

    # ---------------- Map ----------------
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Label('Select Disorder:', className='fw-bold mb-2'),
                    dcc.Dropdown(
                        id='illness-dropdown',
                        options=[{'label': illness_labels[col], 'value': col} for col in illness_cols],
                        value=illness_cols[0],
                        clearable=False
                    ),
                    dcc.Graph(id='map-graph', style={'height': '60vh'}, config={'displayModeBar': False}),
                    html.Label('Year:', className='fw-bold mb-2'),
                    dcc.Slider(
                        id='year-slider',
                        min=min_year,
                        max=max_year,
                        value=max_year,
                        marks={year: str(year) for year in range(min_year, max_year + 1, 5)},
                        step=1,
                        tooltip={'placement': 'bottom', 'always_visible': True}
                    ),

                    # Store the selected country (from map click)
                    dcc.Store(id='selected-country-code', data=default_code)
                ])
            ])
        ], width=12, lg=10, xl=8)
    ], justify='center'),

    # ---------------- Graphs ----------------
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4('Temporal evolution and comparison')), 
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.H5(id='primary-country-name')
                            ])
                        ], md=6),
                        dbc.Col([
                            html.Label('Compare with another country :', className='fw-semibold'),
                            dcc.Dropdown(
                                id='compare-country-dropdown',
                                options=[
                                    {
                                        'label': str(row['country']),
                                        'value': str(row['code'])
                                    }
                                    for _, row in df[['code', 'country']]
                                    .dropna(subset=['code', 'country'])
                                    .drop_duplicates()
                                    .sort_values(by='country')
                                    .iterrows()
                                ],
                                value=None,
                                placeholder='Select country',
                            )
                        ], md=6)
                    ], className='mb-3'),

                    html.Label("Factor(s) :", className='fw-semibold'),
                    dcc.Dropdown(
                        id='indicators-multi',
                        options=[{'label': illness_labels[col], 'value': col} for col in illness_cols],
                        value=['anxiety_disorders'],
                        multi=True,
                        clearable=False
                    ),
                    html.Hr(),
                    html.Div(id='graphs-container')
                ])
            ])
        ], width=12, lg=10, xl=8)
    ], justify='center')

], fluid=True, style={'padding': '20px'})

@app.callback(
    Output('map-graph', 'figure'),
    [Input('illness-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_map(selected_indicator, selected_year):
    filtered_df = df[df['year'] == selected_year].copy()

    if selected_indicator == 'hf_score':
        label = 'HFI score'
    else:
        label = '% of Population'
    
    fig = px.choropleth(
        filtered_df,
        locations='code',
        color=selected_indicator,
        hover_name='country',
        hover_data={selected_indicator: ':.3f', 'code': False},
        color_continuous_scale='Viridis',
        labels={selected_indicator: label}
    )
    
    fig.update_layout(
        title=f'{illness_labels[selected_indicator]} - {selected_year}',
        geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth')
    )
    
    return fig

# Store / update country when clicking the map
@app.callback(
    Output('selected-country-code', 'data'),
    Output('primary-country-name', 'children'),
    Input('map-graph', 'clickData'),
    State('selected-country-code', 'data')
)
def store_selected_country(clickData, current_code):
    code = current_code
    if clickData and 'points' in clickData and len(clickData['points']) > 0:
        pt = clickData['points'][0]
        # px.choropleth uses 'location' to store the ISO code
        code = pt.get('location', current_code)
    name = code_to_name(code) if code else 'No country selected'
    return code, name

# Build one graph per selected indicator
@app.callback(
    Output('graphs-container', 'children'),
    Input('selected-country-code', 'data'),
    Input('compare-country-dropdown', 'value'),
    Input('indicators-multi', 'value')
)
def update_graphs(selected_country, compare_country, indicators):
    graphs = []

    # If no country or no indicator are selected, return empty graph list
    if not selected_country or not indicators:
        return graphs

    # Build indicator figure
    def build_figure(indicator: str):
        df_1 = df[df['code'] == selected_country].sort_values('year') if selected_country else pd.DataFrame()
        df_2 = df[df['code'] == compare_country].sort_values('year') if compare_country else pd.DataFrame()

        # Construct dataframe for graph
        df_graph = []
        if not df_1.empty:
            tmp1 = df_1[['year', indicator]].copy()
            tmp1['Country'] = code_to_name(selected_country)
            df_graph.append(tmp1)
        if not df_2.empty:
            tmp2 = df_2[['year', indicator]].copy()
            tmp2['Country'] = code_to_name(compare_country)
            df_graph.append(tmp2)

        # Return empty graph if no data
        if not df_graph:
            return dcc.Graph(figure=px.line(), config={'displayModeBar': False})

        plot_df = pd.concat(df_graph, ignore_index=True)

        # Calculate y max to manually adjust y axis range
        ymax = float(plot_df[indicator].max()) if not plot_df.empty else 1.0

        if indicator == 'hf_score':
            y_label = 'HFI score'
            hovertemplate = 'Year=%{x}<br>HFI score=%{y:.3f}<extra>%{fullData.name}</extra>'
        else:
            y_label = '% of Population'
            hovertemplate = 'Year=%{x}<br>% of Pop=%{y:.3f}<extra>%{fullData.name}</extra>'

        fig = px.line(
            plot_df,
            x='year', y=indicator, color='Country',
            labels={'year': 'Year', indicator: y_label},
            title=illness_labels[indicator]
        )
        fig.update_traces(
            mode='lines+markers', 
            hovertemplate=hovertemplate
        )

        # Force y axes to start at zero to avoid bias
        fig.update_yaxes(autorange=False, range=[0, ymax * 1.05])
        fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
        return dcc.Graph(figure=fig, style={'height': '320px'}, config={'displayModeBar': False})

    for ind in indicators:
        graphs.append(build_figure(ind))

    return graphs

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(debug=False, host='157.26.83.12', port=52888)