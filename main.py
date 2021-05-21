"""
This file imports the required functions from the other files and libraries and contains the code
which runs the program.

To run the program:
    - Right click to run this file in the Python Console
    - Click the Dash link in the console which will run the program in your browser!

This file is Copyright (c) 2021 Aaditya Mandal, Dinkar Verma, Faraz Hossein, Yousuf Hassan.
"""

from typing import List, Any
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies
import plotly.graph_objects as go
from visualizations import run_visualization, display_empty_plotly_map
from flight_computations import main
from csv_files import get_list, airline_name_to_iata


def airport_airline_options(data_type: str, airports: list, airlines: list) -> List[dict]:
    """Load every airport or airline into a list of dictionaries, depending on the type.

    Preconditions:
        - data_type in {'airports', 'airlines'}
    """
    if data_type == 'airports':
        options, visited = [], []
        for row in airports:
            if str(row[2] + ', ' + row[3]) not in visited:
                visited.append(str(row[2] + ', ' + row[3]))
                options.append({'label': str(row[2] + ', ' + row[3]),
                                'value': str(row[2] + ', ' + row[3])})

        return options

    else:  # if type == 'airlines'
        options, visited = [], []
        for row in airlines:
            if row[1] not in visited and row[7] == 'Y' and row[3] != '' and row[3] != '-':
                visited.append(row[1])
                options.append({'label': row[1], 'value': row[1]})

        return options


def blank_fig() -> object:
    """Return a blank map when the page is first loaded"""
    mapbox_access_token = 'pk.eyJ1IjoieW91c3VmaGFzc2FuMjAiLCJhIjoiY2tuYjYzMT' \
                          'd1MW9qcDJ2cW54MDdkb2RpeCJ9.h4egKfQWUjMYxObNjk0I3w'
    fig = go.Figure()
    fig.add_trace(go.Scattermapbox())
    fig.update_layout(
        hovermode='closest',
        geo=dict(projection_type="equirectangular", showland=True),
        template='plotly_dark',
        margin={'l': 75, 'r': 75, 'b': 75, 't': 75},
        mapbox=dict(
            accesstoken=mapbox_access_token, bearing=0,
            center=dict(lat=0, lon=0),
            pitch=0, zoom=0))

    return fig


def create_app() -> Any:

    """Create and return the app."""
    app = dash.Dash(__name__, prevent_initial_callbacks=True)  # Initializing dash

    # Setting the help icon
    help_image = 'info.png'
    screen = 'info3.png'
    map_icon = 'map.png'

    app.layout = html.Div([  # Div for whole page
        html.Div([  # Div for left side of page
            html.Table([  # Table for left side of page
                html.Td([  # Column for left side of page

                    # Map image
                    html.Img(id='map_image',
                             src=app.get_asset_url(map_icon),
                             style={'width': '30px', 'float': 'right', 'height': '30px',
                                    'cursor': 'pointer'}, n_clicks_timestamp=0),
                    html.Div(id='map_output', style={}),

                    # Help image
                    html.Img(id='help_image',
                             src=app.get_asset_url(help_image),
                             style={'width': '30px', 'float': 'right', 'height': '30px',
                                    'cursor': 'pointer'}, n_clicks_timestamp=0),
                    html.Div(id='img_output', style={}),

                    # First header
                    html.H1('Flight Visualization', id='title', style={'color': '#FFFFFF',
                                                                       'margin-left': '10%',
                                                                       'margin-top': '10%',
                                                                       'display': 'show'}),
                    # Text below header
                    html.P('Please fill out the dropdowns', id='text_below',
                           style={'color': '#FFFFFF', 'margin-left': '10%', 'display': 'show'}),

                    # Number of stops dropdown
                    html.Tr([dcc.Dropdown(id='stops',
                                          options=[{'label': 0, 'value': 0},
                                                   {'label': 1, 'value': 1},
                                                   {'label': 2, 'value': 2}],
                                          style={'width': 200, 'margin-left': '10%',
                                                 'margin-top': '30%',
                                                 'display': 'show'},
                                          placeholder='Number of stops'),
                             html.Div(id='stops_output', style={})],
                            style={}),

                    # Start city dropdown
                    html.Tr([dcc.Dropdown(id='start-city',
                                          options=airport_airline_options(
                                              'airports', airports_list, airlines_list),
                                          style={'width': 200, 'margin-left': '10%',
                                                 'display': 'show'},
                                          placeholder='Origin city'),
                             html.Div(id='start_output', style={})],
                            style={}),

                    # Stop city 1
                    html.Tr([dcc.Dropdown(id='stop_city_1',
                                          options=airport_airline_options(
                                              'airports', airports_list, airlines_list),
                                          style={'width': 200, 'margin-left': '10%',
                                                 'display': 'none'},
                                          placeholder='Stop #1'),
                             html.Div(id='stop_city_1_output', style={})],
                            style={}),

                    # Stop city 2
                    html.Tr([dcc.Dropdown(id='stop_city_2',
                                          options=airport_airline_options(
                                              'airports', airports_list, airlines_list),
                                          style={'width': 200, 'margin-left': '10%',
                                                 'display': 'none'},
                                          placeholder='Stop #2'),
                             html.Div(id='stop_city_2_output', style={})],
                            style={}),

                    # Destination city dropdown
                    html.Tr([dcc.Dropdown(id='end-city',
                                          options=airport_airline_options(
                                              'airports', airports_list, airlines_list),
                                          style={'width': 200, 'margin-left': '10%',
                                                 'display': 'show'},
                                          placeholder='Destination city'),
                             html.Div(id='dest_output', style={})],
                            style={}),

                    # Preferred airline dropdown
                    html.Tr([dcc.Dropdown(id='preferred-airline',
                                          options=airport_airline_options(
                                              'airlines', airports_list, airlines_list),
                                          style={'width': 200, 'margin-left': '10%',
                                                 'display': 'show'},
                                          placeholder='Preferred airline'),
                             html.Div(id='airline_output', style={})],
                            style={}),

                    # View flights button
                    html.Tr([html.Button('View Flights',
                                         id='begin_button',
                                         style={'width': 200, 'margin-left': '20%',
                                                'display': 'show'},
                                         n_clicks_timestamp=0)])],

                        # Styling for left column of page
                        style={})])],

                 # Styling for left side of page
                 style={'max-width': '280px', 'min-width': '280px', 'height': '100%',
                        'background-color': '#000000'}),

        html.Div(
            [dcc.Graph(id='graph_output', style={'height': '100vh'}, figure=blank_fig())],
            id='dcc_div', style={'width': '100%', 'height': '100%', 'display': 'show'}),

        html.Div(
            [html.Img(id='thing', src=app.get_asset_url(screen),
                      style={'width': '100%', 'height': '100vh'})],
            id='info_div',
            style={'width': '100%', 'height': '100%', 'display': 'none'})

    ], style={'width': '100%', 'height': '100%', 'display': 'flex',
              'background-color': '#000000'})

    # Callback to take values of each dropdown
    @app.callback(
        dash.dependencies.Output('graph_output', 'figure'),
        dash.dependencies.Input('begin_button', 'n_clicks_timestamp'),
        dash.dependencies.State('stops', 'value'),
        dash.dependencies.State('stop_city_1', 'value'),
        dash.dependencies.State('stop_city_2', 'value'),
        dash.dependencies.State('start-city', 'value'),
        dash.dependencies.State('end-city', 'value'),
        dash.dependencies.State('preferred-airline', 'value')
    )
    def update_output(n_clicks: Any, input1: Any, input2: Any, input3: Any, input4: Any,
                      input5: Any, input6: Any) -> object:
        """Takes inputted values for each dropdown and returns the appropriate graph.

        NOTES ABOUT pyTA ERRORS:
            pyTA raises the following error for this function:
                The variable update_output is unused and can be removed. If you intended to use it,
                there may be a typo elsewhere in the code.
            However, the python library we are using, Dash, uses update_output, so we do not need
            to call it explicitly in our code.

            pyTA also raises the following error for this function:
                 The parameter 'n_clicks' is unused. This may indicate you misspelled a parameter
                 name in the function body. Otherwise, the parameter can be removed from the
                 function without altering the program.
             However, the python library we are using, Dash, requires this parameter to track
             if the button was clicked or not. So we do not need to call it explicitly in our code.

             Finally, pyTA raises the following error for this function:
                This function has too many parameters (7, exceeding limit 5). You should try to
                reduce the complexity of the function by splitting up it, or combining related
                objects as a single one.
            However, the way the '@app.callback' decorator works is that we need a parameter for
            each input value. In other words, we cannot combine them into a tuple or list to reduce
            the number of parameters; or else, the function will not behave correctly.
        """
        num_stops = input1
        stop_city_1 = input2
        stop_city_2 = input3
        start_city = input4
        end_city = input5
        required_params = (input4, input5, input1, airports_list, routes_list, airlines_list)

        if input6 is None:
            preferred_airline = input6
        else:  # input6 is not None
            preferred_airline = airline_name_to_iata(input6, airlines_list)

        if num_stops is not None and start_city is not None and end_city is not None:

            if stop_city_1 is None and stop_city_2 is None and preferred_airline is not None:
                return run_visualization(main(required_params, airline_choice=preferred_airline))

            elif stop_city_1 is not None and stop_city_2 is None and preferred_airline is not None:
                return run_visualization(
                    main(required_params, stop_c1=stop_city_1, airline_choice=preferred_airline))

            elif stop_city_1 is not None and stop_city_2 is None and preferred_airline is None:
                return run_visualization(main(required_params, stop_c1=stop_city_1))

            elif stop_city_1 is None and stop_city_2 is not None and preferred_airline is None:
                return run_visualization(main(required_params, stop_c2=stop_city_2))

            elif stop_city_1 is None and stop_city_2 is not None and preferred_airline is not None:
                return run_visualization(
                    main(required_params, stop_c2=stop_city_2, airline_choice=preferred_airline))

            elif stop_city_1 is not None and stop_city_2 is not None and preferred_airline is None:
                return run_visualization(
                    main(required_params, stop_c1=stop_city_1, stop_c2=stop_city_2))

            elif stop_city_1 is not None and stop_city_2 is not None and preferred_airline is None:
                return run_visualization(main(required_params,
                                              stop_c1=stop_city_1, stop_c2=stop_city_2,
                                              airline_choice=preferred_airline))

            else:  # stop_city_1 is None and stop_city_2 is None and preferred_airline is None:
                return run_visualization(main(required_params))

        else:
            return display_empty_plotly_map()

    # Callback to determine if info button was clicked
    @app.callback(
        dash.dependencies.Output('dcc_div', component_property='style'),
        dash.dependencies.Output('info_div', component_property='style'),
        dash.dependencies.Output('title', component_property='style'),
        dash.dependencies.Output('text_below', component_property='style'),
        dash.dependencies.Output('stops', component_property='style'),
        dash.dependencies.Output('stop_city_1', component_property='style'),
        dash.dependencies.Output('stop_city_2', component_property='style'),
        dash.dependencies.Output('start-city', component_property='style'),
        dash.dependencies.Output('end-city', component_property='style'),
        dash.dependencies.Output('begin_button', component_property='style'),
        dash.dependencies.Output('preferred-airline', component_property='style'),
        [dash.dependencies.Input('map_image', 'n_clicks_timestamp')],
        [dash.dependencies.Input('help_image', 'n_clicks_timestamp')],
        [dash.dependencies.Input('stops', 'value')]

    )
    def switch_screen(n_clicks_map: Any, n_clicks_help: Any, stops: Any) -> List[dict]:
        """Function to change screens based on which button is clicked.

        If the help button is clicked, this function clears everything on the original screen.
        Otherwise, it shows all the drop down menus and buttons.

        NOTE:
        pyTA raises the following error for this function:
            The variable switch_screen is unused and can be removed. If you intended to use it,
            there may be a typo elsewhere in the code.
        However, the python library we are using, Dash, uses switch_screen, so we do not need to
        call it explicitly in our code.
        """
        if n_clicks_help > n_clicks_map:
            return [
                {'width': '100%', 'height': '100%', 'display': 'none'},
                {'width': '100%', 'height': '100%'},
                {'color': '#FFFFFF', 'margin-left': '10%', 'margin-top': '10%', 'display': 'none'},
                {'color': '#FFFFFF', 'margin-left': '10%', 'display': 'none'},
                {'width': 200, 'margin-left': '10%', 'margin-top': '30%', 'display': 'none'},
                {'width': 200, 'margin-left': '10%', 'display': 'none'},
                {'width': 200, 'margin-left': '10%', 'display': 'none'},
                {'width': 200, 'margin-left': '10%', 'display': 'none'},
                {'width': 200, 'margin-left': '10%', 'display': 'none'},
                {'width': 200, 'margin-left': '20%', 'display': 'none'},
                {'width': 200, 'margin-left': '10%', 'display': 'none'},
            ]
        else:
            if stops == 0:
                return [
                    {'width': '100%', 'height': '100%'},
                    {'width': '100%', 'height': '100%', 'display': 'none'},
                    {'color': '#FFFFFF', 'margin-left': '10%', 'margin-top': '10%'},
                    {'color': '#FFFFFF', 'margin-left': '10%'},
                    {'width': 200, 'margin-left': '10%', 'margin-top': '30%'},
                    {'width': 200, 'margin-left': '10%', 'display': 'none'},
                    {'width': 200, 'margin-left': '10%', 'display': 'none'},
                    {'width': 200, 'margin-left': '10%'},
                    {'width': 200, 'margin-left': '10%'},
                    {'width': 200, 'margin-left': '20%'},
                    {'width': 200, 'margin-left': '10%'},
                ]
            elif stops == 1:
                return [
                    {'width': '100%', 'height': '100%'},
                    {'width': '100%', 'height': '100%', 'display': 'none'},
                    {'color': '#FFFFFF', 'margin-left': '10%', 'margin-top': '10%'},
                    {'color': '#FFFFFF', 'margin-left': '10%'},
                    {'width': 200, 'margin-left': '10%', 'margin-top': '30%'},
                    {'width': 200, 'margin-left': '10%'},
                    {'width': 200, 'margin-left': '10%', 'display': 'none'},
                    {'width': 200, 'margin-left': '10%'},
                    {'width': 200, 'margin-left': '10%'},
                    {'width': 200, 'margin-left': '20%'},
                    {'width': 200, 'margin-left': '10%'},
                ]
            elif stops == 2:
                return [
                    {'width': '100%', 'height': '100%'},
                    {'width': '100%', 'height': '100%', 'display': 'none'},
                    {'color': '#FFFFFF', 'margin-left': '10%', 'margin-top': '10%'},
                    {'color': '#FFFFFF', 'margin-left': '10%'},
                    {'width': 200, 'margin-left': '10%', 'margin-top': '30%'},
                    {'width': 200, 'margin-left': '10%'},
                    {'width': 200, 'margin-left': '10%'},
                    {'width': 200, 'margin-left': '10%'},
                    {'width': 200, 'margin-left': '10%'},
                    {'width': 200, 'margin-left': '20%'},
                    {'width': 200, 'margin-left': '10%'},
                ]
            else:  # if stops is None
                return [
                    {'width': '100%', 'height': '100%'},
                    {'width': '100%', 'height': '100%', 'display': 'none'},
                    {'color': '#FFFFFF', 'margin-left': '10%', 'margin-top': '10%'},
                    {'color': '#FFFFFF', 'margin-left': '10%'},
                    {'width': 200, 'margin-left': '10%', 'margin-top': '30%'},
                    {'width': 200, 'margin-left': '10%', 'display': 'none'},
                    {'width': 200, 'margin-left': '10%', 'display': 'none'},
                    {'width': 200, 'margin-left': '10%'},
                    {'width': 200, 'margin-left': '10%'},
                    {'width': 200, 'margin-left': '20%'},
                    {'width': 200, 'margin-left': '10%'},
                ]

    return app


if __name__ == '__main__':
    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod(verbose=True)

    # import python_ta
    # python_ta.check_all(config={
    #     # the names (strs) of imported modules
    #     'extra-imports': ['dash_core_components', 'dash_html_components', 'dash.dependencies',
    #                       'csv_files', 'visualizations', 'flight_computations',
    #                       'plotly.graph_objects', 'webbrowser'],
    #     'allowed-io': [],  # the names (strs) of functions that call print/open/input
    #     'max-line-length': 100,
    #     'disable': ['E1136']
    # })

    # Running the program
    airports_list = get_list('airports')
    routes_list = get_list('routes')
    airlines_list = get_list('airlines')

    application = create_app()
    application.run_server(debug=False)
