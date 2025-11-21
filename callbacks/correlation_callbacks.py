from dash import Output, Input
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

def register_correlation_callbacks(app, df, correlation_min_year, correlation_max_year):
    @app.callback(
        [Output('corr-graph-1', 'figure'),
        Output('corr-graph-2', 'figure'),
        Output('corr-graph-3', 'figure'),
        Output('corr-graph-4', 'figure'),
        Output('corr-graph-5', 'figure'),
        Output('corr-matrix', 'figure')],
        Input('correlation-year-slider', 'value')
    )
    def update_correlation_graphs(selected_year):
        '''
        Update all correlation graphs
        '''

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
        
        # Graph 3: Mental Disorders vs Alcohol Consumption
        fig3 = px.scatter(
            df_corr,
            y='alcohol_consumption',
            x='global_mental_disorders',
            hover_name='country',
            trendline='ols',
            labels={
                'alcohol_consumption': 'Alcohol consumption (liters)',
                'global_mental_disorders': 'Mental Disorders (% Pop.)'
            },
            title=f'Mental Disorders vs Alcohol consumption ({selected_year})'
        )
        fig3.update_layout(margin=dict(l=10, r=10, t=40, b=10))

        # Graph 4: Mental Disorders vs Gender Inequality Index
        fig4 = px.scatter(
            df_corr,
            y='gii',
            x='global_mental_disorders',
            hover_name='country',
            trendline='ols',
            labels={
                'gii': 'Gender Inequality Index [0,1]',
                'global_mental_disorders': 'Mental Disorders (% Pop.)'
            },
            title=f'Mental Disorders vs Gender Inequality Index ({selected_year})'
        )
        fig4.update_layout(margin=dict(l=10, r=10, t=40, b=10))
        
        # Graph 5: Show correlation coefficients over time
        # Calculate correlations for each year in the range
        years = range(correlation_min_year, correlation_max_year + 1)
        correlations = []
        
        for year in years:
            df_year = df[(df['year'] == year)].dropna(subset=['global_mental_disorders', 'unemployment_rate', 'hf_score', 'alcohol_consumption', 'gii'])
            if len(df_year) > 2:
                corr_unemp = df_year[['global_mental_disorders', 'unemployment_rate']].corr().iloc[0, 1]
                corr_freedom = df_year[['global_mental_disorders', 'hf_score']].corr().iloc[0, 1]
                corr_alcohol = df_year[['global_mental_disorders', 'alcohol_consumption']].corr().iloc[0, 1]
                corr_gii = df_year[['global_mental_disorders', 'gii']].corr().iloc[0, 1]
                correlations.append({
                    'year': year,
                    'Mental vs Unemployment': corr_unemp,
                    'Mental vs Freedom': corr_freedom,
                    'Mental vs Alc. consumption': corr_alcohol,
                    'Mental vs Gender Inequality Index': corr_gii
                })
        
        df_corr_time = pd.DataFrame(correlations)
        
        fig5 = go.Figure()
        fig5.add_trace(go.Scatter(
            x=df_corr_time['year'],
            y=df_corr_time['Mental vs Unemployment'],
            mode='lines+markers',
            name='Mental vs Unemployment'
        ))
        fig5.add_trace(go.Scatter(
            x=df_corr_time['year'],
            y=df_corr_time['Mental vs Freedom'],
            mode='lines+markers',
            name='Mental vs Freedom'
        ))
        fig5.add_trace(go.Scatter(
            x=df_corr_time['year'],
            y=df_corr_time['Mental vs Alc. consumption'],
            mode='lines+markers',
            name='Mental vs Alc. consumption'
        ))
        fig5.add_trace(go.Scatter(
            x=df_corr_time['year'],
            y=df_corr_time['Mental vs Gender Inequality Index'],
            mode='lines+markers',
            name='Mental vs Gender Inequality Index'
        ))
        
        # Add vertical line for selected year
        fig5.add_vline(x=selected_year, line_dash='dash', line_color='red', opacity=0.5)
        
        fig5.update_layout(
            title='Correlation Coefficients Over Time',
            xaxis_title='Year',
            yaxis_title='Correlation Coefficient',
            margin=dict(l=10, r=10, t=40, b=10),
            yaxis=dict(range=[-1, 1])
        )

        # Create correlation matrix
        pretty_names = {
            'schizo_disorders': 'Schizophrenia',
            'depression_disorders': 'Depression',
            'anxiety_disorders': 'Anxiety',
            'bipolar_disorders': 'Bipolar Disorder',
            'eating_disorders': 'Eating Disorders',
            'unemployment_rate': 'Unemployment Rate (%)',
            'hf_score': 'Human Freedom Index',
            'alcohol_consumption': 'Alcohol Consumption (liters)',
            'gii': 'Gender Inequality Index',
            'global_mental_disorders': 'Global Mental Disorders'
        }

        corr_matrix = df_corr.copy()
        corr_matrix = corr_matrix.drop('year', axis=1)
        corr_matrix = corr_matrix.corr(numeric_only=True)

        corr_matrix = corr_matrix.rename(index=pretty_names, columns=pretty_names)

        fig_cm = px.imshow(
            corr_matrix,
             text_auto=".2f",
            aspect='auto',
            color_continuous_scale='RdBu_r',
            zmin=-1, zmax=1
        )

        fig_cm.update_traces(
            hovertemplate='<b>%{x}</b> vs <b>%{y}</b><br>'+
                        'Correlation: <b>%{z:.3f}</b><extra></extra>'
        )

        fig_cm.update_layout(
            title=f'Correlation Matrix ({selected_year})',
            xaxis_title='Variables',
            yaxis_title='Variables'
        )
        
        return fig1, fig2, fig3, fig4, fig5, fig_cm