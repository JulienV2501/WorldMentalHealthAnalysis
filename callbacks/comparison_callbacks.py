from dash import Output, Input, State, dcc, html
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

from utils.helpers import code_to_name

def register_comparison_callbacks(app, df, illness_labels):
    @app.callback(
        Output("compare-country-dropdown", "options"),
        Output("compare-country-dropdown", "disabled"),
        Output("compare-country-dropdown", "value"),
        Input("select-country-dropdown", "value"),
        State("compare-country-dropdown", "value")
    )
    def update_second_dropdown(selected_country_1, selected_country_2):
        # If first dropdown has no value: disable second one
        if selected_country_1 is None:
            return [], True, None

        # Exclude first dropdown value
        new_options=[
            {
                'label': str(row['country']),
                'value': str(row['code'])
            }
            for _, row in (
                df[['code', 'country']]
                .dropna(subset=['code', 'country'])
                .drop_duplicates()
                .sort_values(by='country')
                .iterrows()
            )
            if row['code'] != selected_country_1
        ]

        # Reset if necessary
        if selected_country_2 == selected_country_1:
            selected_country_2 = None

        return new_options, False, selected_country_2


    @app.callback(
        Output('graphs-container', 'children'),
        Input('select-country-dropdown', 'value'),
        Input('compare-country-dropdown', 'value'),
        Input('indicators-multi', 'value')
    )
    def update_comparison_graphs(selected_country, compare_country, indicators):
        '''
        Update and add comparison graphs
        '''

        graphs = []

        if not selected_country or not indicators:
            return graphs

        def build_figure(indicator: str, unit_of_measurement:str):
            '''
            Create time serie individually
            '''

            df_1 = df[df['code'] == selected_country].sort_values('year') if selected_country else pd.DataFrame()
            df_2 = df[df['code'] == compare_country].sort_values('year') if compare_country else pd.DataFrame()

            df_graph = []
            if not df_1.empty:
                tmp1 = df_1[['year', indicator]].copy()
                tmp1['Country'] = code_to_name(df, selected_country)
                df_graph.append(tmp1)
            if not df_2.empty:
                tmp2 = df_2[['year', indicator]].copy()
                tmp2['Country'] = code_to_name(df, compare_country)
                df_graph.append(tmp2)

            if not df_graph:
                return dcc.Graph(figure=px.line(), config={'displayModeBar': False})

            plot_df = pd.concat(df_graph, ignore_index=True)
            ymax = float(plot_df[indicator].max()) if not plot_df.empty else 1.0

            fig = px.line(
                plot_df,
                x='year', y=indicator, color='Country',
                labels={'year': 'Year', indicator: unit_of_measurement},
                title=illness_labels[indicator]
            )
            fig.update_traces(
                mode='lines+markers',
                hovertemplate='Year=%{x}<br>{unit_of_measurement}=%{y:.3f}<extra>%{fullData.name}</extra>'
            )

            fig.update_yaxes(autorange=False, range=[0, ymax * 1.05])
            fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
            return dcc.Graph(figure=fig, style={'height': '320px'}, config={'displayModeBar': False})

        # Loop on selected indactors and create graph
        for ind in indicators:
            unit_of_measurement = '% of Population' if ind != 'global_mental_disorders' else 'global score [0,1]'
            graphs.append(build_figure(ind, unit_of_measurement))

        return graphs
    
    @app.callback(
        Output('radar-graphs-container', 'children'),
        Input('select-country-dropdown', 'value'),
        Input('compare-country-dropdown', 'value'),
        Input('radar-year-slider', 'value')
    )
    def update_radar_graphs(selected_country, compare_country, selected_year):
        '''
        Update radar graphs
        '''

        if not selected_country:
            return None
        
        df_year = df[df['year'] == selected_year].copy()

        c1_row = df_year[df_year['code'] == selected_country]
        c1 = c1_row.iloc[0]

        pretty_names = {
            'unemployment_rate': 'Unemployment (%)',
            'gii': 'Gender Inequality Index',
            'hf_score': 'Human Freedom Index',
            'alcohol_consumption': 'Alcohol Consumption',
            'global_mental_disorders': 'Mental Disorders (Global)'
        }

        indicators = list(pretty_names.keys())
        categories = [pretty_names[i] for i in indicators]

        norm_values = {}

        for ind in indicators:
            min_val = df_year[ind].min()
            max_val = df_year[ind].max()

            c1_val = (c1[ind] - min_val) / (max_val - min_val)

            norm_values[ind] = {'c1': c1_val}

            if compare_country:
                c2_row = df_year[df_year['code'] == compare_country]
                c2 = c2_row.iloc[0]

                c2_val = (c2[ind] - min_val) / (max_val - min_val)

                norm_values[ind]['c2'] = c2_val

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=[norm_values[i]['c1'] for i in pretty_names.keys()],
            theta=categories,
            fill='toself',
            name=code_to_name(df, selected_country),
            line=dict(width=2)
        ))

        if compare_country:
            c2_row = df_year[df_year['code'] == compare_country].iloc[0]
            fig.add_trace(go.Scatterpolar(
                r=[norm_values[i]['c2'] for i in pretty_names.keys()],
                theta=categories,
                fill='toself',
                name=code_to_name(df, compare_country),
                line=dict(width=2)
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 1])
            ),
            title=f'Country Comparison Radar - {selected_year}',
            showlegend=True
        )

        return html.Div([
            dcc.Graph(figure=fig)
        ])