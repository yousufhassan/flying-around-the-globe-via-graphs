"""
This file contains code that imports relevant (and, in a way, the most important) functions from
the other files, and controls the main output of the program.

The user will need to run this file in order to run the program.

This file is Copyright (c) 2021 Aaditya Mandal, Dinkar Verma, Faraz Hossein, Yousuf Hassan.
"""
from typing import Optional, Tuple
import networkx as nx
import graph
from csv_files import airline_name_to_iata


# CONVERTERS BELOW
def airport_iata_to_airport_name(airport_code: str, airports: list) -> str:
    """
    Returns the airport_name from the input of airport_id
    """
    airport_name = ""
    for row in airports:
        if row[4] == airport_code:
            airport_name = row[1]

    return airport_name


def city_to_airports_list(source_city_name: str, airports: list) -> list:
    """Return the airport from the city."""
    lst_of_airports = []

    for row in airports:
        if str(row[2]) + ', ' + str(row[3]) == source_city_name:
            lst_of_airports.append(row[4])

    return lst_of_airports


# main function to make the graph
def load_route_graph(new_route: list[list], airports: list) -> graph.Graph:
    """
    Create the overall graph
    """
    new_graph = graph.Graph()

    for row in new_route:
        # Apparently some route airports aren't in the airports (named different)
        data1 = [row_a for row_a in airports if row_a[4] == row[2]]
        data2 = [row_a for row_a in airports if row_a[4] == row[4]]
        if data1 != [] and data2 != []:
            new_graph.add_vertex(row[2], airports)
            new_graph.add_vertex(row[4], airports)

            new_graph.add_edge(row[2], row[4])

    return new_graph


def load_mini_graph(potential_flights: list[list], n_stops: int) -> nx.DiGraph:
    """Create and return the NetworkX graph based on the potential_flights."""
    gra = nx.DiGraph()

    for trips in potential_flights:
        for i in range(0, n_stops + 2):
            if not isinstance(trips[i + 1], int):
                gra.add_edge(trips[i], trips[i + 1])

    return gra


def zero_stops(required: Tuple[str, str, int, list, list, list],
               airline_choice: Optional[str] = 'None', stop_c1: Optional[str] = 'None',
               stop_c2: Optional[str] = 'None') -> Tuple[nx.DiGraph, graph.Graph, tuple]:
    """Helper function that is called in the main function that calculates and returns the final
    graphs and inputs for direct flights.
    """
    start_city, destination_city, n_stops, airports, routes, airlines = required
    inputs = (start_city, destination_city, n_stops, airline_choice, stop_c1, stop_c2, airlines)

    if airline_choice == 'None':  # Direct Flight with no Airline Choice
        # Making new routes list with the source airport as the starting airport
        all_airports = city_to_airports_list(start_city, airports)
        new_route = [i for i in routes if i[2] in all_airports]

        # Making new graph based on the new_routes
        new_graph = load_route_graph(new_route, airports)

        # Make final mini graph
        nx_graph = load_mini_graph(new_graph.get_trips(required[:4]), n_stops)

        return (nx_graph, new_graph, inputs)

    # Airline Choice=TRUE
    else:

        # Making a new route with only the airline posted
        all_airports = city_to_airports_list(start_city, airports)
        new_route = [i for i in routes if i[2] in all_airports and i[0] == airline_choice]

        # Making new graph based on the new_routes
        new_graph = load_route_graph(new_route, airports)

        nx_graph = load_mini_graph(new_graph.get_trips(required[:4]), n_stops)

        return (nx_graph, new_graph, inputs)


def create_graphs(required: Tuple[str, str, int, list],
                  new_route: list, inputs: tuple) -> Tuple[nx.DiGraph, graph.Graph, tuple]:
    """This is a helper function that is called in one_stop that creates the NetworkX graph
    and graph_initialize graph based on the filtered routes."""

    n_stops, airports = required[2], required[3]

    # Making new graph based on the new_routes
    new_graph = load_route_graph(new_route, airports)

    # Get trips
    p_trips = new_graph.get_trips(required[:4])[:3]
    nx_graph = load_mini_graph(p_trips, n_stops)
    return (nx_graph, new_graph, inputs)


def one_stop(required: Tuple[str, str, int, list, list, list],
             airline_choice: Optional[str] = 'None', stop_c1: Optional[str] = 'None',
             stop_c2: Optional[str] = 'None') -> Tuple[nx.DiGraph, graph.Graph, tuple]:
    """Helper function that is called in the main function that calculates and returns the final
    graphs and inputs for flights with one stop.
    """
    start_city, destination_city, n_stops, airports, routes = required[:5]
    inputs = (start_city, destination_city, n_stops, airline_choice, stop_c1, stop_c2, required[5])

    # Airline Choice=TRUE & Stop Choice=TRUE
    if airline_choice != 'None' and stop_c1 != 'None':
        # Making new routes list with the source airport as the starting airport
        s_airports = city_to_airports_list(start_city, airports)
        t1_airports = city_to_airports_list(stop_c1, airports)
        d_airports = city_to_airports_list(destination_city, airports)
        updated_route = [i for i in routes if i[0] == airline_choice]
        new_route = [i for i in updated_route if i[2] in s_airports and i[4] in t1_airports] + \
                    [i for i in updated_route if i[2] in t1_airports and i[4] in d_airports]

        return create_graphs(required[:4], new_route, inputs)

    # Airline Choice=TRUE & Stop Choice=FALSE
    elif airline_choice != 'None' and stop_c1 == 'None':
        # Making new routes list with the source airport as the starting airport
        s_airports = city_to_airports_list(start_city, airports)
        d_airports = city_to_airports_list(destination_city, airports)
        updated_route = [i for i in routes if i[0] == airline_choice]
        new_route = [i for i in updated_route if i[2] in s_airports] + \
                    [i for i in updated_route if i[4] in d_airports]

        return create_graphs(required[:4], new_route, inputs)

    # Airline Choice=FALSE & Stop Choice=TRUE
    elif airline_choice == 'None' and stop_c1 != 'None':
        # Making new routes list with the source airport as the starting airport
        s_airports = city_to_airports_list(start_city, airports)
        t1_airports = city_to_airports_list(stop_c1, airports)
        d_airports = city_to_airports_list(destination_city, airports)
        new_route = [i for i in routes if i[2] in s_airports and i[4] in t1_airports] + \
                    [i for i in routes if i[2] in t1_airports and i[4] in d_airports]

        return create_graphs(required[:4], new_route, inputs)

    # Airline Choice=FALSE & Stop Choice=FALSE
    else:
        # Making new routes list with the source airport as the starting airport
        s_airports = city_to_airports_list(start_city, airports)
        d_airports = city_to_airports_list(destination_city, airports)
        new_route = [i for i in routes if i[2] in s_airports] + \
                    [i for i in routes if i[4] in d_airports]

        return create_graphs(required[:4], new_route, inputs)


def two_stops(required: Tuple[str, str, int, list, list, list],
              airline_choice: Optional[str] = 'None', stop_c1: Optional[str] = 'None',
              stop_c2: Optional[str] = 'None') -> Tuple[nx.DiGraph, graph.Graph, tuple]:
    """Helper function that is called in the main function that calculates and returns the final
    graphs and inputs for flights with two stops.
    """

    airports, routes = required[3], required[4]
    inputs = (required[0], required[1], required[2], airline_choice, stop_c1, stop_c2, required[5])

    # Airline Choice=FALSE & Stop Choice 1=FALSE & Stop Choice 2=FALSE
    if airline_choice == 'None' and stop_c1 == 'None' and stop_c2 == 'None':
        # Make a new route
        return create_graphs(required[:4], two_stop_helper(required), inputs)

    # Airline Choice=FALSE & Stop Choice 1=TRUE & Stop Choice 2=True
    elif airline_choice == 'None' and stop_c1 != 'None' and stop_c2 != 'None':
        s_airports = city_to_airports_list(required[0], airports)
        t1_airports = city_to_airports_list(stop_c1, airports)
        t2_airports = city_to_airports_list(stop_c2, airports)
        d_airports = city_to_airports_list(required[1], airports)

        s_to_t1 = [i for i in routes if i[2] in s_airports and i[4] in t1_airports]
        t1_to_t2 = [i for i in routes if i[2] in t1_airports and i[4] in t2_airports]
        t2_to_d = [i for i in routes if i[2] in t2_airports and i[4] in d_airports]

        return create_graphs(required[:4], s_to_t1 + t1_to_t2 + t2_to_d, inputs)

    # Airline Choice=TRUE & Stop Choice 1=FALSE & Stop Choice 2=FALSE
    elif airline_choice != 'None' and stop_c1 == 'None' and stop_c2 == 'None':
        return create_graphs(required[:4], [i for i in routes if i[0] == airline_choice], inputs)

    # Airline Choice=TRUE & Stop Choice 1=TRUE & Stop Choice 2=True
    elif airline_choice != 'None' and stop_c1 != 'None' and stop_c2 != 'None':
        s_airports = city_to_airports_list(required[0], airports)
        t1_airports = city_to_airports_list(stop_c1, airports)
        t2_airports = city_to_airports_list(stop_c2, airports)
        d_airports = city_to_airports_list(required[1], airports)

        s_to_t1 = [i for i in routes if i[2] in s_airports and i[4] in t1_airports]
        t1_to_t2 = [i for i in routes if i[2] in t1_airports and i[4] in t2_airports]
        t2_to_d = [i for i in routes if i[2] in t2_airports and i[4] in d_airports]
        no_airline_routes = s_to_t1 + t1_to_t2 + t2_to_d

        return create_graphs(
            required[:4], [i for i in no_airline_routes if i[0] == airline_choice], inputs)

    # If one of stop choice is TRUE, but the other is FALSE
    else:
        return create_graphs(required[:4], [], inputs)


def two_stop_helper(required: Tuple[str, str, int, list, list, list]) -> list:
    """Helper function to find all potential trips for the two stop trip function"""
    main_return = main((required[0], required[1], 1, required[3], required[4], required[5]))

    p_trips = main_return[1].get_trips(
        (required[0], required[1], 1, required[3], required[4], required[5])[:4])[0:5]

    final_routes, stop = [], ''
    visited = list(set([i0[j0] for i0 in
                        [[trip[0], trip[1], trip[2]] for trip in p_trips]
                        for j0 in range(0, len(i0))]))
    # visited = list(set([i[j] for i in
    #                     [[i[0], i[1], i[2]] for i in p_trips]
    #                     for j in range(0, len(i))]))
    for i in p_trips:
        if main_return[1].get_distance(i[0], i[1]) < main_return[1].get_distance(i[1], i[2]):
            stop_finder = 't_to_d'
        else:
            stop_finder = 's_to_t'
        if stop_finder == 't_to_d':
            t_city = main_return[1].get_info(i[1], 'city, country')
            d_city = main_return[1].get_info(i[2], 'city, country')
            required2 = (t_city, d_city, 1, required[3], required[4], required[5])

            stop_p_trips = one_stop(required2)[1].get_trips(required2[:4])
            for j in stop_p_trips:
                if j[1] != p_trips[0] and j[1] != p_trips[2] and j[1] not in visited:
                    stop = j[1]
                    visited.append(stop)
                    break
            final_routes.append([i[0], i[1], stop, i[2]])
        else:  # put in between s_to_d
            s_city = main_return[1].get_info(i[0], 'city, country')
            t_city = main_return[1].get_info(i[1], 'city, country')
            required2 = (s_city, t_city, 1, required[3], required[4], required[5])

            stop_p_trips = one_stop(required2)[1].get_trips(required2[:4])
            for j in stop_p_trips:
                if j[1] != p_trips[0] and j[1] != p_trips[2] and j[1] not in visited:
                    stop = j[1]
                    visited.append(stop)
                    break

            final_routes.append([i[0], stop, i[1], i[2]])

    new_route = []
    for i in range(0, len(final_routes)):
        new_route.append(['AL', 123, final_routes[i][0], 246, final_routes[i][1], 369])
        new_route.append(['AL', 123, final_routes[i][1], 246, final_routes[i][2], 369])
        new_route.append(['AL', 123, final_routes[i][2], 246, final_routes[i][3], 369])

    return new_route


def main(required: Tuple[str, str, int, list, list, list],
         airline_choice: Optional[str] = 'None', stop_c1: Optional[str] = 'None',
         stop_c2: Optional[str] = 'None') -> Tuple[nx.DiGraph, graph.Graph, tuple]:
    """Main Function to run within the visualization.

    The parameter required is a Tuple containing the non-optional parameters. It has the
    following structure:
    (start_city, destination_city, n_stops, airports, routes, airlines)

    Note that required[5] is the airlines dataset as a list. That is only being passed into the
    airline_name_to_iata function, since all other functions do not use it. Therefore, we also only
    pass in required[:5] into the other functions.
    """

    n_stops = required[2]
    airlines = required[5]

    if airline_choice != 'None':
        airline_name_to_iata(airline_choice, airlines)  # might be able to delete this condition

    if n_stops == 0:
        # Airline Choice=FALSE
        return zero_stops(required, airline_choice, stop_c1, stop_c2)

    elif n_stops == 1:
        return one_stop(required, airline_choice, stop_c1, stop_c2)

    else:  # n_stops == 2:
        return two_stops(required, airline_choice, stop_c1, stop_c2)


if __name__ == '__main__':
    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod(verbose=True)

    import python_ta
    python_ta.check_all(config={
        # the names (strs) of imported modules
        'extra-imports': ['graph', 'networkx', 'csv_files', 'visualizations'],
        'allowed-io': [],  # the names (strs) of functions that call print/open/input
        'max-line-length': 100,
        'disable': ['E1136']
    })
