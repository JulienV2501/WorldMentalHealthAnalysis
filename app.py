from dash import Dash, dcc, html
import dash_bootstrap_components as dbc

from utils.data_loader import load_data
from utils.indexMentalHealth import indexMentalHealth
from utils.constants import illness_labels, illness_cols

from callbacks.intro_callbacks import register_intro_callbacks
from callbacks.comparison_callbacks import register_comparison_callbacks
from callbacks.correlation_callbacks import register_correlation_callbacks

# Load data
df = load_data(save_as_file=False)
df = indexMentalHealth(df)

# Set parameters
min_year = int(df['year'].min())
max_year = int(df['year'].max())

correlation_min_year = 2000
correlation_max_year = 2019

default_code = None

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([

    # ---------------- Title ----------------
    dbc.Row([
        dbc.Col([
            html.H1('Mental Health Disorders by Country', className='text-center mb-4')
        ])
    ]),

    # ---------------- Intro (map + bar plots) ----------------
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
                    html.Label('Year:', className='fw-bold mb-2'),
                    dcc.Slider(
                        id='year-slider',
                        min=min_year,
                        max=max_year,
                        value=max_year,
                        marks={year: str(year) for year in range(min_year, max_year + 1, 5)},
                        step=1,
                        tooltip={'placement': 'bottom', 'always_visible': True},
                        className='mb-4'
                    ),

                    dcc.Graph(id='map-graph', style={'height': '60vh'}, config={'displayModeBar': False}),
                    dcc.Store(id='selected-country-code', data=default_code),

                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(
                                id='continent-bar',
                                style={'height': '400px'},
                                config={'displayModeBar': False}
                            )
                        ], width=6),
                        dbc.Col([
                            dcc.Graph(
                                id='income-bar',
                                style={'height': '400px'},
                                config={'displayModeBar': False}
                            )
                        ], width=6)
                    ], justify='center', className='mb-4'),

                    dcc.Graph(id='global-evolution-graph', style={'height': '500px'}, config={'displayModeBar': False})
                ])
            ])
        ], width=12, lg=10, xl=8)
    ], justify='center', className='mb-4'),


    # ---------------- Country Comparison Graphs ----------------
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
                            html.Label('Compare with another country:', className='fw-semibold'),
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
                    html.Label('Factor(s):', className='fw-semibold'),
                    dcc.Dropdown(
                        id='indicators-multi',
                        options=[{'label': illness_labels[col], 'value': col} for col in illness_cols],
                        value=['anxiety_disorders'],
                        multi=True,
                        clearable=False
                    ),
                    html.Hr(),
                    html.Div(id='graphs-container'),

                    html.Hr(),
                    dcc.Slider(
                        id='radar-year-slider',
                        min=correlation_min_year,
                        max=correlation_max_year,
                        value=correlation_max_year,
                        marks={year: str(year) for year in range(correlation_min_year, correlation_max_year + 1, 5)},
                        step=1,
                        tooltip={'placement': 'bottom', 'always_visible': True},
                        className='mb-4'
                    ),
                    html.Div(id='radar-graphs-container')
                ])
            ])
        ], width=12, lg=10, xl=8)
    ], justify='center'),
    
    html.Br(),
    
    # ---------------- Correlation Analysis ----------------
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4('Global Correlations: Mental Health, Unemployment & Freedom')),
                dbc.CardBody([
                    html.Label('Year:', className='fw-bold mb-2'),
                    dcc.Slider(
                        id='correlation-year-slider',
                        min=correlation_min_year,
                        max=correlation_max_year,
                        value=correlation_max_year,
                        marks={year: str(year) for year in range(correlation_min_year, correlation_max_year + 1, 5)},
                        step=1,
                        tooltip={'placement': 'bottom', 'always_visible': True}
                    ),
                    html.Hr(),
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='corr-graph-1', config={'displayModeBar': False})
                        ], md=6),
                        dbc.Col([
                            dcc.Graph(id='corr-graph-2', config={'displayModeBar': False})
                        ], md=6)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='corr-graph-3', config={'displayModeBar': False})
                        ], md=6),
                        dbc.Col([
                            dcc.Graph(id='corr-graph-4', config={'displayModeBar': False})
                        ], md=6)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='corr-graph-5', config={'displayModeBar': False})
                        ], md=12)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='corr-matrix', config={'displayModeBar': False})
                        ], md=12)
                    ])
                ])
            ])
        ], width=12, lg=10, xl=8)
    ], justify='center', className='mb-4')

], fluid=True, style={'padding': '20px'})

# Register callbacks function
register_intro_callbacks(app, df, illness_labels)
register_comparison_callbacks(app, df, illness_labels)
register_correlation_callbacks(app, df, correlation_min_year, correlation_max_year)

if __name__ == '__main__':
    app.run(debug=True)