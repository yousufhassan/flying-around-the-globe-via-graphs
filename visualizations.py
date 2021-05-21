"""
This file has all the code that creates the NetworkX graph and visualizes the results using
plotly and mapbox.

This file is Copyright (c) 2021 Aaditya Mandal, Dinkar Verma, Faraz Hossein, Yousuf Hassan.
"""
from typing import Dict, Tuple
import networkx as nx
import plotly.graph_objects as go
import graph
from csv_files import airline_iata_to_name


def create_pos_dict(nx_graph: nx.DiGraph,
                    full_graph: graph.Graph) -> Dict[str, Tuple[float, float]]:
    """Creates and returns a dictionary with airports IATAs as keys and its coordinates
     as values.

     coords_dict takes the format {'IATA': (latitude, longitude)}.

     NOTE: For the NetworkX graph, we may need the corresponding coords to be flipped, but for
     plotly/mapbox the regular order is required.
     If anything, we can make a dict for both cases, and return a tuple containing the two dicts.
     """
    coords_dict = {}
    airports = list(nx_graph.nodes)
    for airport in airports:
        lat = float(full_graph.get_info(airport, 'position')[0])
        long = float(full_graph.get_info(airport, 'position')[1])

        coords_dict[airport] = (lat, long)

    return coords_dict


def update_graph_coords(pos_dict: Dict[str, Tuple[float, float]], nx_graph: nx.DiGraph) -> None:
    """Takes all the coordinate values from pos_dict and updates the 'pos' value for each
    NetworkX node airport.
    """
    for iata, coordinate in pos_dict.items():
        nx_graph.nodes[iata]['pos'] = coordinate


def add_mapbox_nodes(map_fig: go.Figure, pos_dict: Dict[str, Tuple[float, float]],
                     r_graph: graph.Graph()) -> None:
    """Helper function for display_plotly_map that adds the airports (nodes) to the map."""
    lats = [pos_dict[iata][0] for iata in pos_dict]
    lons = [pos_dict[iata][1] for iata in pos_dict]

    airport_names = [r_graph.get_info(iata, 'name') for iata in list(pos_dict.keys())]
    iata_list = list(pos_dict.keys())
    city_names = [r_graph.get_info(iata, 'city') for iata in list(pos_dict.keys())]
    country_names = [r_graph.get_info(iata, 'country') for iata in list(pos_dict.keys())]
    airport_info = []

    # This loop combines all the information from the lists above and appends it as elements of
    # airport_info, which is displayed on the map when you hover over an airport.
    for i in range(0, len(airport_names)):
        airport_info.append(airport_names[i] + ' (' + iata_list[i] + ')' + '<br>' + city_names[i]
                            + ', ' + country_names[i]
                            + '<br>' + str([pos_dict[iata] for iata in pos_dict][i]))

    map_fig.add_trace(go.Scattermapbox(name='airports', lat=lats, lon=lons, mode='markers',
                                       marker=go.scattermapbox.Marker(size=15, color='cadetblue'),
                                       hoverinfo='text',
                                       text=airport_info,))


def add_mapbox_edges(map_fig: go.Figure, pos_dict: Dict[str, Tuple[float, float]],
                     nx_graph: nx.DiGraph) -> None:
    """Helper function for display_plotly_map that adds the flight routes (edges) to the map."""
    edges = list(nx_graph.edges)
    line_attributes = {'color': 'gold'}

    # Add flight route edges
    for i in range(len(nx_graph.edges)):
        route_name = list(nx_graph.edges)[i][0] + ' --> ' + list(nx_graph.edges)[i][1]
        middle_lat = [(pos_dict[edges[i][0]][0] + pos_dict[edges[i][1]][0]) / 2]
        middle_lon = [(pos_dict[edges[i][0]][1] + pos_dict[edges[i][1]][1]) / 2]
        map_fig.add_trace(go.Scattermapbox(name=route_name,
                                           lat=[pos_dict[edges[i][0]][0], pos_dict[edges[i][1]][0]],
                                           lon=[pos_dict[edges[i][0]][1], pos_dict[edges[i][1]][1]],
                                           mode='lines',
                                           line=line_attributes))

        # Adding the transparent nodes in the middle of each edge, for the purpose of labeling
        map_fig.add_trace(go.Scattermapbox(lat=middle_lat, lon=middle_lon, mode='markers',
                                           marker=go.scattermapbox.Marker(opacity=0, size=15,
                                                                          color='gold'),
                                           showlegend=False,
                                           hoverinfo='text',
                                           text=route_name))


def generate_plotly_map_name(inputs: tuple) -> str:
    """This is helper function for display_plotly_map which generates and returns the plotly map
    name based on the input values.
    """
    airline_name = airline_iata_to_name(inputs[3], inputs[6])
    if airline_name == 'None':  # no specific airline
        if inputs[2] == 0:  # direct flight
            map_title = 'Best direct flights from ' + inputs[0] + ' to ' + inputs[1]

        elif inputs[2] == 1:  # flights with 1 stop
            map_title = 'Best flights from ' + inputs[0] + ' to ' + inputs[1] + \
                        ' with ' + str(inputs[2]) + ' stop'

        else:  # inputs[2] > 1 (flights with more than one stop)
            map_title = 'Best flights from ' + inputs[0] + ' to ' + inputs[1] + \
                        ' with ' + str(inputs[2]) + ' stops'

    else:  # airline_name != 'None'  (if there is a specific airline)
        if inputs[2] == 0:  # direct flight
            map_title = 'Best ' + airline_name + ' direct flights from ' + inputs[0] + ' to ' \
                        + inputs[1]

        elif inputs[2] == 1:  # flights with 1 stop
            map_title = 'Best ' + airline_name + ' flights from ' + inputs[0] + ' to ' \
                        + inputs[1] + ' with ' + str(inputs[2]) + ' stop'

        else:  # inputs[2] > 1 (flights with more than one stop)
            map_title = 'Best ' + airline_name + ' flights from ' + inputs[0] + ' to ' \
                        + inputs[1] + ' with ' + str(inputs[2]) + ' stops'

    return map_title


def display_plotly_map(pos_dict: Dict[str, Tuple[float, float]], nx_graph: nx.DiGraph,
                       r_graph: graph.Graph(), inputs: tuple) -> go.Figure:
    """This function creates and plots the airports and best flight routes on a map, using mapbox
    and plotly.

    The mapbox_access_token was obtained by making a free account for mapbox.com. It is the public
    token for my account, so I believe it will work from any computer running this function.
    """
    mapbox_access_token = 'pk.eyJ1IjoieW91c3VmaGFzc2FuMjAiLCJhIjoiY2tuYjYzMT' \
                          'd1MW9qcDJ2cW54MDdkb2RpeCJ9.h4egKfQWUjMYxObNjk0I3w'
    # Create map
    map_fig = go.Figure()
    add_mapbox_edges(map_fig, pos_dict, nx_graph)
    add_mapbox_nodes(map_fig, pos_dict, r_graph)

    # Plotly map title based on different input values
    map_title = generate_plotly_map_name(inputs)

    # Display final graph output on a map
    map_fig.update_layout(
        title=map_title,
        hovermode='closest',
        geo=dict(projection_type="equirectangular", showland=True,),
        template='plotly_dark',
        mapbox=dict(
            accesstoken=mapbox_access_token, bearing=0,
            center=dict(lat=0, lon=0),
            pitch=0, zoom=0))

    return map_fig


def display_empty_plotly_map() -> go.Figure:
    """This function creates and plots an empty map, if there are no possible flight routes for
    the selected input configuration.

    The mapbox_access_token was obtained by making a free account for mapbox.com. It is the public
    token for my account, so I believe it will work from any computer running this function.
    """
    mapbox_access_token = 'pk.eyJ1IjoieW91c3VmaGFzc2FuMjAiLCJhIjoiY2tuYjYzMT' \
                          'd1MW9qcDJ2cW54MDdkb2RpeCJ9.h4egKfQWUjMYxObNjk0I3w'
    # Create map
    map_fig = go.Figure()
    map_fig.add_trace(go.Scattermapbox())  # add an empty trace

    # Display final graph output on a map
    map_fig.update_layout(
        title='There are no flights with your current inputted configuration!',
        hovermode='closest',
        geo=dict(projection_type="equirectangular", showland=True,),
        template='plotly_dark',
        mapbox=dict(
            accesstoken=mapbox_access_token, bearing=0,
            center=dict(lat=0, lon=0),
            pitch=0, zoom=0))

    return map_fig


def run_visualization(main_input: Tuple[nx.DiGraph, graph.Graph, tuple]) -> go.Figure:
    """This function creates NetworkX graph based on the source_city, dest_city, and number of
    stops, and then calls all the functions that output the graph using mapbox/plotly.

    If the graphs are empty, that means there are no flight routes for the current input
    configurations, so an empty map is displayed.
    """
    nx_graph, full_graph, inputs = main_input

    pos_dict = create_pos_dict(nx_graph, full_graph)
    update_graph_coords(pos_dict, nx_graph)

    if list(nx_graph.nodes) == []:
        return display_empty_plotly_map()
    else:
        return display_plotly_map(pos_dict, nx_graph, full_graph, inputs)


if __name__ == '__main__':
    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod(verbose=True)

    import python_ta
    python_ta.check_all(config={
        # the names (strs) of imported modules
        'extra-imports': ['graph', 'networkx', 'plotly.graph_objects', 'csv_files'],
        'allowed-io': [],  # the names (strs) of functions that call print/open/input
        'max-line-length': 100,
        'disable': ['E1136']
    })
