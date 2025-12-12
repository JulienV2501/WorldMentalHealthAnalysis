from dash import Output, Input
import plotly.express as px
import plotly.graph_objects as go

def register_intro_callbacks(app, df, illness_labels):
    @app.callback(
        [Output('map-graph', 'figure'),
        Output('continent-bar', 'figure'),
        Output('income-bar', 'figure')],
        [Input('illness-dropdown', 'value'),
        Input('year-slider', 'value')]
    )
    def update_map_and_bar_plot(selected_indicator, selected_year):
        '''
        Update map and continent/income bar plots graphs
        '''

        filtered_df = df[df['year'] == selected_year].copy()

        unit_of_measurement = '% of Population' if selected_indicator != 'global_mental_disorders' else 'global score [0,1]'
        
        # --- Map ---
        fig_map = px.choropleth(
            filtered_df,
            locations='code',
            color=selected_indicator,
            hover_name='country',
            color_continuous_scale='Viridis',
            labels={selected_indicator: unit_of_measurement}
        )
        
        fig_map.update_traces(
            hovertemplate='<b>%{hovertext}</b><br>' + unit_of_measurement + ': %{z:.2f}<extra></extra>'
        )
        
        fig_map.update_layout(
            title=f'{illness_labels[selected_indicator]} - {selected_year}',
            geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth')
        )

        # --- Bar plot (continent) ---
        df_cont = filtered_df[filtered_df['country'].isin(['Africa', 'Asia', 'Europe', 'America'])]
        df_cont = df_cont.sort_values(by=selected_indicator, ascending=False)

        fig_cont = px.bar(
            df_cont,
            x='country', 
            y=selected_indicator,
            color='country',
            text_auto='.2f',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            title='Average by continent',
            labels={selected_indicator: unit_of_measurement, 'country': ''}
        )

        fig_cont.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title=None,
            yaxis_title=unit_of_measurement,
            margin=dict(l=50, r=20, t=50, b=60)
        )
        fig_cont.update_traces(hoverinfo='skip', hovertemplate=None)

        # --- Bar plot (income) ---
        income_labels = ['Low-income countries', 'Lower-middle-income countries',
                        'Upper-middle-income countries', 'High-income countries']
        df_income = filtered_df[filtered_df['country'].isin(income_labels)]
        df_income = df_income.sort_values(by=selected_indicator, ascending=False)

        df_income['country'] = df_income['country'].str.replace(' countries', '').str.replace('-income', '').str.title()

        fig_income = px.bar(
            df_income,
            x='country',
            y=selected_indicator,
            color='country',
            text_auto='.2f',
            color_discrete_sequence=px.colors.qualitative.Set2,
            title='Average by countries income group',
            labels={'country': '', selected_indicator: unit_of_measurement}
        )
        
        fig_income.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis_title=unit_of_measurement,
            margin=dict(l=50, r=20, t=50, b=60)
        )
        fig_income.update_traces(hoverinfo='skip', hovertemplate=None)
        
        return fig_map, fig_cont, fig_income
    
    @app.callback(
        Output('global-evolution-graph', 'figure'),
        [Input('illness-dropdown', 'value'),
        Input('year-slider', 'value')]
    )
    def update_global_evolution(selected_illness, selected_year):
        '''
        Update intro global evolution (top/bottom countries)
        '''

        unit_of_measurement = '% of Population' if selected_illness != 'global_mental_disorders' else 'global score [0,1]'
        
        filtered_df = df[df['year'] == selected_year].copy()

        mean_by_country = (
            filtered_df.groupby(['code', 'country'])[selected_illness]
            .first()
            .sort_values(ascending=False)
        )
        top10 = mean_by_country.head(10).reset_index()
        bottom10 = mean_by_country.tail(10).reset_index()

        fig = go.Figure()

        # --- Top 10 bars ---
        fig.add_trace(go.Bar(
            x=top10['code'],
            y=top10[selected_illness],
            name='Top 10 countries',
            marker_color='rgba(30, 150, 255, 0.6)',
            showlegend=True,
            xaxis='x',
            yaxis='y',
            hovertext=top10['country'],
            hovertemplate=f'%{{hovertext}}<br>{unit_of_measurement} = %{{y:.3f}}<extra></extra>'
        ))

        # --- Bottom 10 bars ---
        fig.add_trace(go.Bar(
            x=bottom10['code'],
            y=bottom10[selected_illness],
            name='Bottom 10 countries',
            marker_color='rgba(255, 160, 30, 0.6)',
            showlegend=True,
            xaxis='x',
            yaxis='y',
            hovertext=bottom10['country'],
            hovertemplate=f'%{{hovertext}}<br>{unit_of_measurement} = %{{y:.3f}}<extra></extra>'
        ))

        fig.update_layout(
            title=f'{illness_labels[selected_illness]} - Overall trend and representation of the most/least affected countries',

            yaxis=dict(
                title=unit_of_measurement,
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
                title='',
                showticklabels=False,
                showgrid=False,
                showline=False, 
            ),

            barmode='group', 
            bargap=0.1,
            legend=dict(orientation='h', y=-0.25),
            margin=dict(l=50, r=30, t=60, b=60),
            plot_bgcolor='rgba(255,255,255,1)'
        )

        return fig