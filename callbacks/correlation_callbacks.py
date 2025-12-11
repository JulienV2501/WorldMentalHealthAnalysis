from dash import Output, Input
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def make_scatter(df, x, y, title, labels):
    fig = px.scatter(
        df,
        x=x,
        y=y,
        hover_name='country',
        trendline='ols',
        labels=labels,
        title=title
    )

    fig.update_traces(
        marker=dict(
            size=8,
            opacity=0.6,
            line=dict(width=0)
        )
    )

    fig.update_layout(
        margin=dict(l=10, r=10, t=40, b=10),
        plot_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="lightgrey", griddash="dash", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="lightgrey", griddash="dash", zeroline=False),
        title={
            "text": fig.layout.title.text,
            "font": {"size": 14, "color": "black"}
        }
    )

    return fig


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
        fig1 = make_scatter(
            df_corr,
            x="global_mental_disorders",
            y="unemployment_rate",
            title=f"Global Mental Dis. vs Unemployment ({selected_year})",
            labels={
                "unemployment_rate": "Unemployment Rate (%)",
                "global_mental_disorders": "Global Mental Disorders"
            }
        )
        
        # Graph 2: Mental Disorders vs Freedom Index
        fig2 = make_scatter(
            df_corr,
            x="global_mental_disorders",
            y="hf_score",
            title=f"Global Mental Dis. vs Freedom ({selected_year})",
            labels={
                "hf_score": "Human Freedom Index",
                "global_mental_disorders": "Global Mental Disorders"
            }
        )
        
        # Graph 3: Mental Disorders vs Alcohol Consumption
        fig3 = make_scatter(
            df_corr,
            x="global_mental_disorders",
            y="alcohol_consumption",
            title=f"Global Mental Dis. vs Alcohol cons. ({selected_year})",
            labels={
                "alcohol_consumption": "Alcohol consumption (liters)",
                "global_mental_disorders": "Global Mental Disorders"
            }
        )

        # Graph 4: Mental Disorders vs Gender Inequality Index
        fig4 = make_scatter(
            df_corr,
            x="global_mental_disorders",
            y="gii",
            title=f"Global Mental Dis. vs Gender Inequality ({selected_year})",
            labels={
                "gii": "Gender Inequality Index [0,1]",
                "global_mental_disorders": "Global Mental Disorders"
            }
        )
        
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
                    'Global Mental Dis. vs Unemployment rate': corr_unemp,
                    'Global Mental Dis. vs Freedom Index': corr_freedom,
                    'Global Mental Dis. vs Alcohol cons.': corr_alcohol,
                    'Global Mental Dis. vs Gender Inequality Index': corr_gii
                })
        
        df_corr_time = pd.DataFrame(correlations)
        
        fig5 = go.Figure()

        fig5.add_trace(go.Scatter(
            x=df_corr_time['year'],
            y=df_corr_time['Global Mental Dis. vs Unemployment rate'],
            mode='lines+markers',
            name='Global Mental Dis. vs Unemployment rate',
            marker_symbol='circle',
            marker_size=8,
            marker_color='#0072B2',
            line=dict(color='#0072B2')
        ))
        fig5.add_trace(go.Scatter(
            x=df_corr_time['year'],
            y=df_corr_time['Global Mental Dis. vs Freedom Index'],
            mode='lines+markers',
            name='Global Mental Dis. vs Freedom Index',
            marker_symbol='square',
            marker_size=8,
            marker_color='#D55E00',
            line=dict(color='#D55E00')
        ))
        fig5.add_trace(go.Scatter(
            x=df_corr_time['year'],
            y=df_corr_time['Global Mental Dis. vs Alcohol cons.'],
            mode='lines+markers',
            name='Global Mental Dis. vs Alcohol cons.',
            marker_symbol='triangle-up',
            marker_size=8,
            marker_color='#009E73',
            line=dict(color='#009E73')
        ))
        fig5.add_trace(go.Scatter(
            x=df_corr_time['year'],
            y=df_corr_time['Global Mental Dis. vs Gender Inequality Index'],
            mode='lines+markers',
            name='Global Mental Dis. vs Gender Inequality Index',
            marker_symbol='diamond',
            marker_size=8,
            marker_color='#CC79A7',
            line=dict(color='#CC79A7')
        ))

        # Add vertical line for selected year
        fig5.add_vline(x=selected_year, line_dash='dash', line_color='red', opacity=0.6)

        fig5.add_hline(
            y=0,
            line_dash='dash',
            line_color='black',
            opacity=0.3
        )
        
        fig5.update_layout(
            title='Correlation Coefficients Over Time',
            height=500,
            xaxis_title='Year',
            yaxis_title='Correlation Coefficient',
            margin=dict(l=10, r=10, t=120, b=10),
            yaxis=dict(range=[-1, 1]),
            paper_bgcolor='white',
            plot_bgcolor='white',
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1,
                xanchor='center',
                x=0.5
            )
        )

        # Create correlation matrix
        pretty_names = {
            'schizo_disorders': 'Schizophrenia',
            'depression_disorders': 'Depression',
            'anxiety_disorders': 'Anxiety',
            'bipolar_disorders': 'Bipolar Dis.',
            'eating_disorders': 'Eating Dis.',
            'unemployment_rate': 'Unemploy. (%)',
            'hf_score': 'Human Free.',
            'alcohol_consumption': 'Alcohol Cons.',
            'gii': 'Gender Ineq.',
            'global_mental_disorders': 'Global Mental Dis.'
        }

        corr_matrix = df_corr.copy()
        corr_matrix = corr_matrix.drop('year', axis=1)
        corr_matrix = corr_matrix.corr(numeric_only=True)

        corr_matrix = corr_matrix.rename(index=pretty_names, columns=pretty_names)

        diag_mask = np.eye(corr_matrix.shape[0], dtype=bool)
        corr_matrix.values[diag_mask] = -999  # special code for diagonal

        custom_scale = [
            [0.00, 'white'],
            [0.001, '#005fb8'],
            [0.50, '#E0E0E0'],
            [1.00, '#cc0000']
        ]

        text_matrix = corr_matrix.round(2).astype(str)
        # Remove diagonal values
        for i in range(len(text_matrix)):
            text_matrix.iat[i, i] = ""

        fig_cm = px.imshow(
            corr_matrix,
            aspect='auto',
            color_continuous_scale=custom_scale,
            zmin=-1, zmax=1
        )

        fig_cm.update_traces(
            text=text_matrix,
            texttemplate="%{text}",
            hovertemplate='<b>%{x}</b> vs <b>%{y}</b><br>'+
                        'Correlation: <b>%{z:.3f}</b><extra></extra>'
        )

        fig_cm.update_xaxes(showgrid=False)
        fig_cm.update_yaxes(showgrid=False)

        fig_cm.update_layout(
            title=f'Correlation Matrix ({selected_year})',
            xaxis_title='Indicators',
            yaxis_title='Indicators'
        )
        
        return fig1, fig2, fig3, fig4, fig5, fig_cm