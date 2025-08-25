# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Launch Site dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] +
                [{'label': s, 'value': s} for s in sorted(spacex_df['Launch Site'].unique())],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: range slider for payload
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        value=[min_payload, max_payload],
        marks={0: '0', 2500: '2.5k', 5000: '5k', 7500: '7.5k', 10000: '10k'}
    ),

    # TASK 4: scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # суммарные успешные пуски по площадкам
        fig = px.pie(
            spacex_df, values='class', names='Launch Site',
            title='Total Successful Launches by Site'
        )
        return fig
    else:
        # успех/провал для выбранной площадки
        df_site = spacex_df[spacex_df['Launch Site'] == entered_site]
        counts = (df_site['class']
                  .replace({1: 'Success', 0: 'Failure'})
                  .value_counts()
                  .reset_index())
        counts.columns = ['Outcome', 'Count']
        fig = px.pie(
            counts, values='Count', names='Outcome',
            title=f'Success vs Failure for {entered_site}'
        )
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter(selected_site, payload_range):
    lo, hi = payload_range
    df_f = spacex_df[(spacex_df['Payload Mass (kg)'] >= lo) &
                     (spacex_df['Payload Mass (kg)'] <= hi)]
    if selected_site != 'ALL':
        df_f = df_f[df_f['Launch Site'] == selected_site]

    fig = px.scatter(
        df_f,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site'],
        title=('Payload vs Success (All Sites)'
               if selected_site == 'ALL'
               else f'Payload vs Success ({selected_site})')
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run()
