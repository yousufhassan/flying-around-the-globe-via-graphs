"""
This file contains the _Vertex and Graph classes. Each vertex is an airport, while edges represent
flight routes between airports.

The _Vertex class is inspired by the one covered in class, but it has been changed to reflect the
needs for an airport object.
The Graph class is based off the one covered in the course, but with several additional methods
that are relevant for flights, airports, etc.

This file is Copyright (c) 2021 Aaditya Mandal, Dinkar Verma, Faraz Hossein, Yousuf Hassan.
"""
from __future__ import annotations
from typing import Any, Tuple, List
import math
# from csv_files import get_list


def get_airports(city: str, airports: list) -> list:
    """Return all existing airports per given a specific city"""
    lst_of_airports = []

    for row in airports:
        if str(row[2] + ', ' + row[3]) == city:
            lst_of_airports.append(row[4])

    return lst_of_airports


def two_stop_trip_helper(x_value: str, d_value: str, routes: list) -> list:
    """helper for the two stop trip function"""
    visited = []
    t = []
    # routes = get_list('routes')
    for row_2 in routes:
        if d_value == row_2[2] and (x_value, d_value, row_2[4]) not in visited:
            t.append((x_value, d_value, row_2[4]))
            visited.append((x_value, d_value, row_2[4]))
    return t


class _Vertex:
    """A vertex in a the graph representing an airport.

    Instance Attributes:
        - iata: The data stored in this vertex, representing the iata(id) of the airport.
        - name: Name of the airport
        - city: City that the airport is located in
        - country: Country that the airport is located in
        - position: Latitude and Longitude of the Airport [Latidude: float, Longitude: float]
        - neighbours: The vertices that are adjacent to this vertex.

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)

    """
    iata: Any
    name: str
    city: str
    country: str
    position: [float, float]
    neighbours: set[_Vertex]

    def __init__(self, item: Any, airports: list) -> None:
        """Initialize a new vertex with the given item and kind.

        This vertex is initialized with no neighbours.

        Preconditions:
            - ...
        """
        # airports = get_list('airports')
        data = [row for row in airports if row[4] == item]
        self.iata = item
        self.name = data[0][1]
        self.city = data[0][2]
        self.country = data[0][3]
        self.position = [data[0][6], data[0][7]]
        self.neighbours = set()


class Graph:
    """A graph used to represent a book review network.
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _Vertex object.
    _vertices: dict[Any, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def add_vertex(self, item: Any, airports: list) -> None:
        """Add a vertex with the given item and kind to this graph.

        The new vertex is not adjacent to any other vertices.
        Do nothing if the given item is already in this graph.

        Preconditions:
            - kind in {'user', 'book'}
        """
        if item not in self._vertices:
            self._vertices[item] = _Vertex(item, airports)

    def add_edge(self, item1: Any, item2: Any) -> None:
        """Add an edge between the two vertices with the given items in this graph.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            v1.neighbours.add(v2)
            v2.neighbours.add(v1)
        else:
            raise ValueError

    def adjacent(self, item1: Any, item2: Any) -> bool:
        """Return whether item1 and item2 are adjacent vertices in this graph.

        Return False if item1 or item2 do not appear as vertices in this graph.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            return any(v2.iata == item2 for v2 in v1.neighbours)
        else:
            return False

    def get_neighbours(self, item: Any) -> set:
        """Return a set of the neighbours of the given item.

        Note that the *items* are returned, not the _Vertex objects themselves.

        Raise a ValueError if item does not appear as a vertex in this graph.
        """
        if item in self._vertices:
            v = self._vertices[item]
            return {neighbour.iata for neighbour in v.neighbours}
        else:
            raise ValueError

    def get_all_vertices(self) -> set:
        """Return a set of all vertex items in this graph.

        If kind != '', only return the items of the given vertex kind.

        Preconditions:
            - kind in {'', 'user', 'book'}
        """
        return {v.iata for v in self._vertices.values()}

    def get_info(self, iata: str, info_type: str) -> Any:
        """Function to retrieve information about an airport from iata.

        Preconditions:
            - info_type in {'name', 'city', 'country', 'position', 'city, country'}
        """
        if info_type == 'name':
            return self._vertices[iata].name
        elif info_type == 'city':
            return self._vertices[iata].city
        elif info_type == 'country':
            return self._vertices[iata].country
        elif info_type == 'position':
            return self._vertices[iata].position
        elif info_type == 'city, country':
            return self._vertices[iata].city + ', ' + self._vertices[iata].country
        else:
            return ""

    def get_time(self, source_airport_iata: str, dest_airport_iata: str) -> int:
        """Calculate the ETA from the longitude and latitude of the airports"""
        source_lat = float(self.get_info(source_airport_iata, 'position')[0])
        source_long = float(self.get_info(source_airport_iata, 'position')[1])
        dest_lat = float(self.get_info(dest_airport_iata, 'position')[0])
        dest_long = float(self.get_info(dest_airport_iata, 'position')[1])

        distance = haversine_calculator([source_lat, source_long], [dest_lat, dest_long])

        # Assuming the plane takes 10 minutes to reach cruising altitude and land
        # Assuming the average cruising speed is 925.373
        # THIS TIME IS VERY APPROXIMATE
        time = ((distance / 925.373) * 60) + 20
        return round(time)

    def get_distance(self, source_airport_iata: str, dest_airport_iata: str) -> int:
        """Calculate the distance from the longitude and latitude of the airports"""
        source_lat = float(self.get_info(source_airport_iata, 'position')[0])
        source_long = float(self.get_info(source_airport_iata, 'position')[1])
        dest_lat = float(self.get_info(dest_airport_iata, 'position')[0])
        dest_long = float(self.get_info(dest_airport_iata, 'position')[1])

        return round(haversine_calculator([source_lat, source_long], [dest_lat, dest_long]))

    def direct_trip(self, start: str, end: str) -> List[list]:
        """
        Create all possible paths with no stops in the middle (direct)
        """
        paths = []
        if start in self._vertices and end in self._vertices:
            if self.adjacent(start, end):
                time = self.get_time(start, end)
                distance = self.get_distance(start, end)
                paths.append([start, end, time, distance])

            return paths
        else:
            return []

    def one_stop_trip(self, start: str, end: str) -> List[list]:
        """
        Create all possible paths with one stop in the middle
        """
        paths = []
        if start in self._vertices and end in self._vertices:
            start_n = list(self.get_neighbours(start))
            for i in start_n:
                if end in self.get_neighbours(i):
                    time = self.get_time(start, i) + self.get_time(i, end)
                    distance = self.get_distance(start, i) + self.get_distance(i, end)
                    paths.append([start, i, end, distance, time])

            return paths
        else:
            return []

    def two_stop_trip(self, start: str, end: str, airports: list) -> List[list]:
        """
        Create all possible paths with two stops in the middle

        Work that needs to still be done
            - Account for Airlines (optional value)
            - Account for duplicate airports
                - some trips are devious so like Toronto to Montreal will do this
                    - Airport in Toronto -> Airport in London -> Airport back in Toronto
                            -> then Toronto to Montreal... only some tho
        """
        paths = []
        visited = []
        if start in self._vertices and end in self._vertices:
            for i in list(self.get_neighbours(start)):
                for j in list(self.get_neighbours(i)):
                    self.two_stop_trip_helper((start, end, i, j), visited, paths, airports)
            return paths
        else:
            return []

    def two_stop_trip_helper(self, string_airports: Tuple[str, str, str, str],
                             visited: list, paths: list, airports: list) -> None:
        """This is a helper function that simplifies the code in two_stop_trip."""
        start, end, i, j = string_airports
        if end in self.get_neighbours(j) and i not in visited and j not in visited:
            visited += get_airports(self.get_info(i, 'city, country'), airports)
            visited += get_airports(self.get_info(j, 'city, country'), airports)
            time = self.get_time(start, i) + self.get_time(i, j) + self.get_time(j, end)
            distance = self.get_distance(start, i) + self.get_distance(
                i, j) + self.get_distance(j, end)
            paths.append([start, i, j, end, distance, time])

    def get_trips(self, required: Tuple[str, str, int, list]) -> List[list]:
        """Returns the best top 3 trips based on the number of stops.

        required has the following structure:
        (start_city, destination_city, num_stops, airports, routes)
        """
        s_city, d_city, stops, airports = required

        potential_flights = []
        source_airports = get_airports(s_city, airports)
        dest_airports = get_airports(d_city, airports)

        # direct trip (works for all)
        if stops == 0:
            for i in source_airports:
                for j in dest_airports:
                    potential_flights += (self.direct_trip(i, j))

        # one stop trip (works for all)
        elif stops == 1:
            for i in source_airports:
                for j in dest_airports:
                    potential_flights += (self.one_stop_trip(i, j))

            # visited_stops = []
            # for i in range(0, len(potential_flights) - 1):
            #     if potential_flights[i][1] in visited_stops:
            #         potential_flights.pop(i)
            #     else:
            #         visited_stops.append(potential_flights[i][1])

        # # two stop trip (works for all)
        elif stops == 2:
            for i in source_airports:
                for j in dest_airports:
                    potential_flights += self.two_stop_trip(i, j, airports)

        potential_flights.sort(key=lambda flights: flights[stops + 2])
        return potential_flights


def haversine_calculator(source_airport: list, dest_airport: list) -> float:
    """Using the longitude and latitude of two airports, this function will return the distance,
    using the Haversine Formula.
    """
    source_lat, source_long = source_airport[0], source_airport[1]
    dest_lat, dest_long = dest_airport[0], dest_airport[1]

    radius = 6371

    dlat = math.radians(dest_lat - source_lat)
    dlon = math.radians(dest_long - source_long)

    # Separating the two terms for clarity
    m1 = math.cos(math.radians(source_lat))
    m2 = math.cos(math.radians(dest_lat)) * math.sin(dlon / 2) * math.sin(dlon / 2)

    t1 = math.sin(dlat / 2) * math.sin(dlat / 2)
    t2 = m1 * m2

    part_a = t1 + t2
    part_b = 2 * math.atan2(math.sqrt(part_a), math.sqrt(1 - part_a))

    return radius * part_b


if __name__ == '__main__':
    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod(verbose=True)

    import python_ta
    python_ta.check_all(config={
        # the names (strs) of imported modules
        'extra-imports': ['csv_files', 'math'],
        'allowed-io': [],  # the names (strs) of functions that call print/open/input
        'max-line-length': 100,
        'disable': ['E1136']
    })
