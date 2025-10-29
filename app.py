import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
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
    'global_mental_disorders'
]

illness_labels = {
    illness_cols[0]: 'Schizophrenia disorders',
    illness_cols[1]: 'Depressive Disorders',
    illness_cols[2]: 'Anxiety Disorders',
    illness_cols[3]: 'Bipolar Disorders',
    illness_cols[4]: 'Eating Disorders',
    illness_cols[5]: 'Global Mental Disorders',

}

min_year = int(df['year'].min())
max_year = int(df['year'].max())

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1('Mental Health Disorders by Country', className='text-center mb-4')
        ])
    ]),
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
                    )
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
def update_map(selected_illness, selected_year):
    filtered_df = df[df['year'] == selected_year].copy()
    
    fig = px.choropleth(
        filtered_df,
        locations='code',
        color=selected_illness,
        hover_name='country',
        hover_data={selected_illness: ':.3f', 'code': False},
        color_continuous_scale='Viridis',
        labels={selected_illness: '% of Population'}
    )
    
    fig.update_layout(
        title=f'{illness_labels[selected_illness]} - {selected_year}',
        geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth')
    )
    
    return fig

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(debug=False, host='157.26.83.12', port=52888)