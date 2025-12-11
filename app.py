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

    # ---------------- Global title & intro ----------------
    dbc.Row([
        dbc.Col([
            html.H1('World Mental Health Analysis', className='text-center mt-3 mb-3 fw-bold'),
            html.P(
                """
                This dashboard explores the global evolution of mental health disorders across countries. 
                It allows users to visualize disorder prevalence over time,
                compare nations, and identify correlations with socioeconomic indicators such as unemployment, human freedom and alcool consumption.
                 The goal is to provide an intuitive and data-driven view of a link between different indicators and mental health.
                """,
                className='text-center mb-4 fs-5',
                style={'maxWidth': '900px', 'margin': 'auto'}
            )
        ])
    ]),


    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4('Indicators')),
                dbc.CardBody([
                html.Div([
                    html.Ul([
                        html.Li([
                            html.B("Freedom Index: "),
                            "Composite index evaluating political rights, civil liberties, and overall democratic freedom. "
                            "Higher values represent countries where individuals enjoy more personal and societal freedoms."
                        ]),
                        html.Li([
                            html.B("Alcohol Consumption: "),
                            "Average annual liters of pure alcohol consumed per adult (15+). "
                            "This is a health and behavioral indicator often correlated with social patterns and well-being."
                        ]),
                        html.Li([
                            html.B("Gender Inequality Index: "),
                            "Measures inequality in reproductive health, empowerment, and labor market participation. "
                            "Higher values indicate greater inequality between men and women."
                        ]),
                    ], style={"fontSize": "14px"})
                ], className="mb-4")
            ])
        ])
    ], width=12, lg=10, xl=8),
    ], justify='center', className='mb-4'),

    # ---------------- Intro (map + bar plots) ----------------
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4('Mental Health Disorders by Country')),
                dbc.CardBody([

                    html.P(
                        """
                        This section provides a global overview of mental health disorders. 
                        Use the controls below to select a specific disorder and year, then explore 
                        how its prevalence varies across the world, continents, and income groups,
                        as well as its global evolution over time.
                        """,
                        className='text-muted'
                    ),

                    html.Label('Select Disorder:', className='fw-bold mb-2 mt-2'),
                    dcc.Dropdown(
                        id='illness-dropdown',
                        options=[{'label': illness_labels[col], 'value': col} for col in illness_cols],
                        value=illness_cols[0],
                        clearable=False
                    ),

                    html.Label('Year:', className='fw-bold mb-2 mt-3'),
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

                    # Map
                    html.H5('Global prevalence map', className='mt-3'),
                    html.P(
                        """
                        The map shows the estimated prevalence of the selected mental health disorder 
                        in each country for the chosen year. Darker colors generally indicate higher 
                        prevalence values.
                        """,
                        className='text-muted small'
                    ),
                    dcc.Graph(
                        id='map-graph',
                        style={'height': '60vh'},
                        config={'displayModeBar': False}
                    ),

                    # Continent vs income bars
                    dbc.Row([

                        dbc.Col([
                            html.H6('Average by continent', className='mt-3'),
                            html.P(
                                """
                                This bar chart aggregates countries by continent and displays the 
                                average prevalence of the selected disorder for the chosen year.
                                """,
                                className='text-muted small'
                            ),
                            dcc.Graph(
                                id='continent-bar',
                                style={'height': '400px'},
                                config={'displayModeBar': False}
                            )
                        ], width=6),

                        dbc.Col([
                            html.H6('Average by income group', className='mt-3'),
                            html.P(
                                """
                                This bar chart groups countries by income level (e.g. low, middle, high income) 
                                and shows the average disorder prevalence for each group.
                                """,
                                className='text-muted small'
                            ),
                            dcc.Graph(
                                id='income-bar',
                                style={'height': '400px'},
                                config={'displayModeBar': False}
                            )
                        ], width=6)

                    ], justify='center', className='mb-4'),
                    dcc.Graph(
                        id='global-evolution-graph',
                        style={'height': '500px'},
                        config={'displayModeBar': False}
                    )
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

                    html.P(
                        """
                        This section focus on specific countries and compare their mental health 
                        trends over time. You can analyse one country in detail or compare it with another 
                        country on multiple mental health indicators.
                        """,
                        className='text-muted'
                    ),

                    dbc.Row([
                        dbc.Col([
                            html.Label('Select country to analyse evolution:', className='fw-semibold mt-2'),
                            dcc.Dropdown(
                                id='select-country-dropdown',
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
                                placeholder='Select first country',
                            )
                        ], md=6),

                        dbc.Col([
                            html.Label('(Optional) Compare with another country:', className='fw-semibold mt-2'),
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
                                placeholder='Select second country',
                                disabled=True
                            )
                        ], md=6)
                    ], className='mb-3'),

                    html.Div(
                        id="analysis-section",
                        children=[
                            html.Label('Factor(s):', className='fw-semibold'),
                            html.P(
                                """
                                Select one or several mental health indicators to include in the comparison 
                                (e.g. anxiety disorders, depressive disorders).
                                """,
                                className='text-muted small'
                            ),
                            dcc.Dropdown(
                                id='indicators-multi',
                                options=[{'label': illness_labels[col], 'value': col} for col in illness_cols],
                                value=['anxiety_disorders'],
                                multi=True,
                                clearable=False
                            ),

                            html.Hr(),

                            html.H5('Time series for selected country(ies)'),
                            html.Div(id='graphs-container'),

                            html.Hr(),

                            html.H5('Radar chart for a specific year', className='mt-3'),
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

                            html.Div(id='radar-graphs-container'),
                        ],
                        style={"display": "none"}
                    ),

                    html.Div([
                        html.H6("Additional indicators explained:", className="mt-3 mb-2"),
                        html.Ul([
                            html.Li([
                                html.B("Freedom Index: "),
                                "Composite index evaluating political rights, civil liberties, and overall democratic freedom. "
                                "Higher values represent countries where individuals enjoy more personal and societal freedoms."
                            ]),
                            html.Li([
                                html.B("Alcohol Consumption: "),
                                "Average annual liters of pure alcohol consumed per adult (15+). "
                                "This is a health and behavioral indicator often correlated with social patterns and well-being."
                            ]),
                            html.Li([
                                html.B("Gender Inequality Index: "),
                                "Measures inequality in reproductive health, empowerment, and labor market participation. "
                                "Higher values indicate greater inequality between men and women."
                            ]),
                        ], style={"fontSize": "14px"})
                    ], className="mb-4")

                    
                ])
            ])
        ], width=12, lg=10, xl=8)
    ], justify='center'),
    
    html.Br(),
    
    # ---------------- Correlation Analysis ----------------
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4('Global Correlations')),
                dbc.CardBody([

                    html.P(
                        """
                        This section explores how mental health indicators relate to unemployment,
                        freedom and other socioeconomic variables. Use the year slider to update
                        all correlation plots and the correlation matrix.
                        """,
                        className='text-muted'
                    ),

                    html.Label('Year:', className='fw-bold mb-2 mt-2'),
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