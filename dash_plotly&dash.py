import pandas as pd 
import numpy as np

import dash 
from dash import html
from dash import dcc 
from dash.dependencies import Input, Output, State 

import plotly.graph_objects as go
import plotly.express as px
px.defaults.color_discrete_sequence = px.colors.qualitative.Set3


app = dash.Dash(__name__)

server = app.server

# Clear the layout and do not display exception till callback gets executed
app.config.suppress_callback_exceptions = True

# Import data
data = pd.read_csv('AB_NYC_2019.csv')

# Data preparation 
data.reviews_per_month.fillna(0, inplace=True)

app.layout = html.Div(id='main_div', children=[
    # Header 
    html.H1(['New York City', html.Span(' AirBnB ', style={'color':'#ED6664'}), 'Analytics Dashboard'],
            style={'textAlign':'center'}),

    # Main division, containing drop-down title, drop-down, small dataset summary, and graphs 
    html.Div([
        # First inner division, containing drop-down title 
        html.Div(
            html.H3('Choose neighbourhood group(s)', style={'textAlign':'center'})
            ),

        # Second inner division, containing drop-down
        dcc.Dropdown(
            id='drop_down_nh_groups',
            options=[
                {'label':'All', 'value':['Brooklyn', 'Manhattan', 'Queens', 'Staten Island', 'Bronx']},
                {'label':'Brooklyn', 'value':'Brooklyn'},
                {'label':'Manhattan', 'value':'Manhattan'},
                {'label':'Queens', 'value':'Queens'},
                {'label':'Staten Island', 'value':'Staten Island'},
                {'label':'Bronx', 'value':'Bronx'}
            ],
            placeholder="Select a neighbourhood group",
            value=[''],
            style={'width':'50%', 'margin':['0 auto']}
        ),

        # Third division, containing dataset summary
        html.Div(id='dataset_summary', children=[
            html.Div([
                html.P('Number of Listings:'),
                html.P('', id='p1')
            ]),
            html.Div([
                html.P('Number of Hosts:'),
                html.P('', id='p2')
            ]),
            html.Div([
                html.P('Number of Neighbourhoods:'),
                html.P('', id='p3')
            ])
        ]),

        # Forth division, containing graphs 
        html.Div(id='plots_div', children=[
            html.Div([ ], id='plot1'),
            html.Div([ ], id='plot2'),
            html.Div([ ], id='plot3'),
            html.Div([ ], id='plot4'),
            html.Div([ ], id='plot5')
            ])

    ]) 
    # The end of the main division

])
# Layout ends

@app.callback(
    [
        Output(component_id='plot1', component_property='children'),
        Output(component_id='plot2', component_property='children'),
        Output(component_id='plot3', component_property='children'),
        Output(component_id='plot4', component_property='children'),
        Output(component_id='plot5', component_property='children'),
        Output(component_id='p1', component_property='children'),
        Output(component_id='p2', component_property='children'),
        Output(component_id='p3', component_property='children')
    ],
    Input(component_id='drop_down_nh_groups', component_property='value')
)

def display_graphs(value): 
    if type(value) == str:
        value_list = []
        value_list.append(value)
    else:
        value_list = value
    filtered_df = data.loc[data.neighbourhood_group.isin(value_list)].copy()

    # Plot1
    fig1 = px.scatter_mapbox(filtered_df, lat='latitude', lon='longitude', color='neighbourhood',  
                  hover_name='name', hover_data=['neighbourhood_group'], zoom=10)
    
    fig1.update_traces(showlegend=False)
    fig1.update_layout(mapbox_style='carto-positron')

    # Plot2
    fig2 = px.histogram(filtered_df, x='price', title='Average home/apartment/room price')

    mean = round(filtered_df.price.mean(), 2)
    median = filtered_df.price.median()
    mode = round((filtered_df.price).mode()[0],2)

    fig2.add_vline(x=median, line_dash="dash", line_color="green", annotation_text=f"Median: {median}")
    fig2.add_vline(x=mean, line_dash="dash", line_color="red", annotation_text=f"Mean: {mean}",
                annotation_y=0.9)
    fig2.add_vline(x=mode, line_dash="dash", line_color="purple", annotation_text=f"Mode: {mode}", 
                annotation_position='top left')

    fig2.update_annotations(font=dict(color='black', size=15))
    fig2.update_layout(title_x=0.5)
    fig2.update_xaxes(title_text="Price")
    fig2.update_yaxes(title_text="")

    # Plot3
    RT = pd.DataFrame(
                    dict(
                        Room_Type = filtered_df.room_type.value_counts().index,
                        RT_Count=filtered_df.room_type.value_counts().values,
                        RT_Percent=(pd.Series(filtered_df['room_type'].value_counts(normalize=True).values)).apply(
                                    lambda x: f'{x*100:.1f}%').values)
                    )
    
    fig3 = px.bar(data_frame=RT, x='Room_Type', y='RT_Count',
                  text='RT_Percent', title='Number of listings by the room type', 
                  color=['#8dd3c7', '#ffffb3', '#bebada'])
    fig3.update_traces(showlegend=False)
    fig3.update_layout(title_x=0.5)
    fig3.update_xaxes(title_text="Room types")
    fig3.update_yaxes(title_text="")

    # Plot4    
    fig4 = px.histogram(filtered_df, x='minimum_nights', title='Minimum number of nights per listing')

    fig4.update_traces(xbins=dict(start=0, end=51, size=1))
    fig4.update_layout(title_x=0.5)
    fig4.update_xaxes(title_text="Minimum Nights")
    fig4.update_yaxes(title_text="")

    # Plot5
    fig5 = px.histogram(filtered_df, x='number_of_reviews', title='Number of reviews per listing')

    fig5.update_traces(xbins=dict(start=0, end=51, size=1))
    fig5.update_layout(title_x=0.5)
    fig5.update_xaxes(title_text="Number of reviews")
    fig5.update_yaxes(title_text="")

    fig1.update_layout(margin={"r":1,"l":1, "t":1, "b":1})
    fig2.update_layout(margin={"r":25,"l":0})
    fig3.update_layout(margin={"r":25,"l":0})
    fig4.update_layout(margin={"r":25,"l":0})
    fig5.update_layout(margin={"r":25,"l":0})

    # Filling spans with dataset summary
    num_listings = filtered_df.shape[0]
    num_hosts = filtered_df.host_id.nunique()
    num_nh = filtered_df.neighbourhood.nunique()

    return [dcc.Graph(figure=fig1),
            dcc.Graph(figure=fig2),
            dcc.Graph(figure=fig3),
            dcc.Graph(figure=fig4),
            dcc.Graph(figure=fig5),
            f'{num_listings}',
            f'{num_hosts}',
            f'{num_nh}'
            ]

if __name__ == '__main__':
    app.run_server()