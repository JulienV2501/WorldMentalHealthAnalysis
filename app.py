import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

from data_loader import load_data
from indexMentalHealth import indexMentalHealth

df = load_data(save_as_file=False)
df = indexMentalHealth(df)

# Only mental disorders for the main map
illness_cols = [
    'schizo_disorders',
    'depression_disorders',
    'anxiety_disorders',
    'bipolar_disorders',
    'eating_disorders',
    'global_mental_disorders'
]

illness_labels = {
    illness_cols[0]: 'Schizophrenia disorders',
    illness_cols[1]: 'Depressive Disorders',
    illness_cols[2]: 'Anxiety Disorders',
    illness_cols[3]: 'Bipolar Disorders',
    illness_cols[4]: 'Eating Disorders',
    illness_cols[5]: 'Global Mental Disorders'
}

# Extended labels for correlation graphs
all_labels = {
    **illness_labels,
    'unemployment_rate': 'Unemployment Rate',
    'hf_score': 'Human Freedom Index'
}

min_year = int(df['year'].min())
max_year = int(df['year'].max())

# For correlation section: 2000-2022
correlation_min_year = 2000
correlation_max_year = 2019

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
                        tooltip={'placement': 'bottom', 'always_visible': True},
                        className='mb-4'
                    ),
                    dcc.Store(id='selected-country-code', data=default_code),

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
                    html.Label("Factor(s):", className='fw-semibold'),
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
                        ], md=12)
                    ])
                ])
            ])
        ], width=12, lg=10, xl=8)
    ], justify='center', className='mb-4'),

], fluid=True, style={'padding': '20px'})

@app.callback(
    Output('map-graph', 'figure'),
    [Input('illness-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_map(selected_indicator, selected_year):
    filtered_df = df[df['year'] == selected_year].copy()
    
    fig = px.choropleth(
        filtered_df,
        locations='code',
        color=selected_indicator,
        hover_name='country',
        hover_data={selected_indicator: ':.3f', 'code': False},
        color_continuous_scale='Viridis',
        labels={selected_indicator: '% of Population'}
    )
    
    fig.update_layout(
        title=f'{illness_labels[selected_indicator]} - {selected_year}',
        geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth')
    )
    
    return fig

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
        code = pt.get('location', current_code)
    name = code_to_name(code) if code else 'No country selected'
    return code, name

@app.callback(
    [Output('corr-graph-1', 'figure'),
     Output('corr-graph-2', 'figure'),
     Output('corr-graph-3', 'figure')],
    Input('correlation-year-slider', 'value')
)
def update_correlation_graphs(selected_year):
    # Filter data for selected year and valid range
    df_corr = df[(df['year'] == selected_year) & 
                 (df['year'] >= correlation_min_year) & 
                 (df['year'] <= correlation_max_year)].copy()
    
    # Drop rows with missing data
    df_corr = df_corr.dropna(subset=['global_mental_disorders', 'unemployment_rate', 'hf_score'])
    
    # Graph 1: Mental Disorders vs Unemployment
    fig1 = px.scatter(
        df_corr,
        y='unemployment_rate',
        x='global_mental_disorders',
        hover_name='country',
        trendline='ols',
        labels={
            'unemployment_rate': 'Unemployment Rate (%)',
            'global_mental_disorders': 'Mental Disorders (% Pop.)'
        },
        title=f'Mental Disorders vs Unemployment ({selected_year})'
    )
    fig1.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    
    # Graph 2: Mental Disorders vs Freedom Index
    fig2 = px.scatter(
        df_corr,
        y='hf_score',
        x='global_mental_disorders',
        hover_name='country',
        trendline='ols',
        labels={
            'hf_score': 'Human Freedom Index',
            'global_mental_disorders': 'Mental Disorders (% Pop.)'
        },
        title=f'Mental Disorders vs Freedom ({selected_year})'
    )
    fig2.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    
    
    # Graph 4: Show correlation coefficients over time
    # Calculate correlations for each year in the range
    years = range(correlation_min_year, correlation_max_year + 1)
    correlations = []
    
    for year in years:
        df_year = df[(df['year'] == year)].dropna(subset=['global_mental_disorders', 'unemployment_rate', 'hf_score'])
        if len(df_year) > 2:
            corr_unemp = df_year[['global_mental_disorders', 'unemployment_rate']].corr().iloc[0, 1]
            corr_freedom = df_year[['global_mental_disorders', 'hf_score']].corr().iloc[0, 1]
            correlations.append({
                'year': year,
                'Mental vs Unemployment': corr_unemp,
                'Mental vs Freedom': corr_freedom
            })
    
    df_corr_time = pd.DataFrame(correlations)
    
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=df_corr_time['year'],
        y=df_corr_time['Mental vs Unemployment'],
        mode='lines+markers',
        name='Mental vs Unemployment'
    ))
    fig3.add_trace(go.Scatter(
        x=df_corr_time['year'],
        y=df_corr_time['Mental vs Freedom'],
        mode='lines+markers',
        name='Mental vs Freedom'
    ))
    
    # Add vertical line for selected year
    fig3.add_vline(x=selected_year, line_dash='dash', line_color='red', opacity=0.5)
    
    fig3.update_layout(
        title='Correlation Coefficients Over Time',
        xaxis_title='Year',
        yaxis_title='Correlation Coefficient',
        margin=dict(l=10, r=10, t=40, b=10),
        yaxis=dict(range=[-1, 1])
    )
    
    return fig1, fig2, fig3

@app.callback(
    Output('graphs-container', 'children'),
    Input('selected-country-code', 'data'),
    Input('compare-country-dropdown', 'value'),
    Input('indicators-multi', 'value')
)
def update_graphs(selected_country, compare_country, indicators):
    graphs = []

    if not selected_country or not indicators:
        return graphs

    def build_figure(indicator: str):
        df_1 = df[df['code'] == selected_country].sort_values('year') if selected_country else pd.DataFrame()
        df_2 = df[df['code'] == compare_country].sort_values('year') if compare_country else pd.DataFrame()

        df_graph = []
        if not df_1.empty:
            tmp1 = df_1[['year', indicator]].copy()
            tmp1['Country'] = code_to_name(selected_country)
            df_graph.append(tmp1)
        if not df_2.empty:
            tmp2 = df_2[['year', indicator]].copy()
            tmp2['Country'] = code_to_name(compare_country)
            df_graph.append(tmp2)

        if not df_graph:
            return dcc.Graph(figure=px.line(), config={'displayModeBar': False})

        plot_df = pd.concat(df_graph, ignore_index=True)
        ymax = float(plot_df[indicator].max()) if not plot_df.empty else 1.0

        fig = px.line(
            plot_df,
            x='year', y=indicator, color='Country',
            labels={'year': 'Year', indicator: '% of Population'},
            title=illness_labels[indicator]
        )
        fig.update_traces(
            mode='lines+markers',
            hovertemplate='Year=%{x}<br>% of Pop=%{y:.3f}<extra>%{fullData.name}</extra>'
        )

        fig.update_yaxes(autorange=False, range=[0, ymax * 1.05])
        fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
        return dcc.Graph(figure=fig, style={'height': '320px'}, config={'displayModeBar': False})

    for ind in indicators:
        graphs.append(build_figure(ind))

    return graphs

@app.callback(
    Output('global-evolution-graph', 'figure'),
    Input('illness-dropdown', 'value')
)
def update_global_evolution(selected_illness):
    world_trend = (
        df.groupby('year')[selected_illness]
        .mean()
        .reset_index()
        .rename(columns={selected_illness: 'GlobalMean'})
    )

    
    mean_by_country = (
        df.groupby(['code', 'country'])[selected_illness]
        .mean()
        .sort_values(ascending=False)
    )
    top10 = mean_by_country.head(10).reset_index()
    bottom10 = mean_by_country.tail(10).reset_index()

    fig = go.Figure()

    # --- Top 10 bars ---
    fig.add_trace(go.Bar(
        x=top10['code'],
        y=top10[selected_illness],
        name='Top 10 countries (avg)',
        marker_color='rgba(30, 150, 255, 0.6)',
        showlegend=True,
        xaxis='x',
        yaxis='y',
        hovertext=top10['country'],
        hovertemplate='%{hovertext}<br>Avg % of Population = %{y:.3f}<extra></extra>'
    ))

    # --- Bottom 10 bars ---
    fig.add_trace(go.Bar(
        x=bottom10['code'],
        y=bottom10[selected_illness],
        name='Bottom 10 countries (avg)',
        marker_color='rgba(255, 160, 30, 0.6)',
        showlegend=True,
        xaxis='x',
        yaxis='y',
        hovertext=bottom10['country'],
        hovertemplate='%{hovertext}<br>Avg % of Population = %{y:.3f}<extra></extra>'
    ))

    # --- Global curve ---
    fig.add_trace(go.Scatter(
        x=world_trend['year'],
        y=world_trend['GlobalMean'],
        mode='lines+markers',
        name='Global Average (yearly)',
        line=dict(color='black', width=3),
        xaxis='x2',
        yaxis='y',
        hovertemplate='Year %{x}<br>Avg % of Population = %{y:.3f}<extra></extra>'
    ))

    fig.update_layout(
        title=f"{illness_labels[selected_illness]} — Overall trend and representation of the most/least affected countries",

        yaxis=dict(
            title='% of Population',
            rangemode='tozero'
        ),

        xaxis=dict(
            domain=[0, 1],
            anchor='y',
            title='Countries (averages)',
            tickangle=30
        ),

        xaxis2=dict(
            domain=[0, 1],
            anchor='y',
            overlaying='x',
            side='top',
            title='Years (global evolution)',
            tickmode='linear',
            dtick=2,
            showgrid=False,
        ),

        barmode='group', 
        bargap=0.1,
        legend=dict(orientation='h', y=-0.25),
        margin=dict(l=50, r=30, t=130, b=60),
        plot_bgcolor='rgba(255,255,255,1)'
    )

    return fig

if __name__ == '__main__':
    app.run(debug=True)