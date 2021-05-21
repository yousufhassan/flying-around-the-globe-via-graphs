"""
This file handles all the code related to the csv files.

One of its main purposes is to read the data from the multiple csv files, and store them as lists.

This file is Copyright (c) 2021 Aaditya Mandal, Dinkar Verma, Faraz Hossein, Yousuf Hassan.
"""
import csv


def csv_to_list(file: str) -> list:
    """Read the entries from the csv file and return the data in a list.
    """
    lst = []

    with open(file, 'r', encoding='UTF-8') as csv_file:
        reader = csv.reader(csv_file)
        count = 0

        for row in reader:
            if count == 0:
                count += 1
            else:
                lst.append(row)

    return lst


def get_list(list_data: str) -> list:
    """This function returns a list containing the appropriate list_data

    Preconditions:
        - list_data in {'airports', 'airlines', 'routes'}
    """

    if list_data == 'airports':
        airports = csv_to_list('data/airports.csv')
        return airports
    elif list_data == 'airlines':
        airlines = csv_to_list('data/airlines.csv')
        return airlines
    else:  # list_data == 'routes'
        routes = csv_to_list('data/routes.csv')
        return routes


def airline_name_to_iata(airline_name: str, airlines: list) -> str:
    """This function converts the airline_name to its IATA value and returns it.

    Preconditions:
        - airline_name in [airline[1] for airline in airlines]
    """
    for airline in airlines:
        if airline[1] == airline_name:
            return airline[3]

    # This line of code will actually never be reached due to the function precondition, but it
    # is just here to satisfy a pyTA error.
    return 'None'


def airline_iata_to_name(airline_iata: str, airlines: list) -> str:
    """This function converts the airline_iata to its actual name and returns it.

    Preconditions:
        - airline_name in [airline[3] for airline in airlines]
    """
    for airline in airlines:
        if airline[3] == airline_iata:
            return airline[1]

    # This line of code will actually never be reached due to the function precondition, but it
    # is just here to satisfy a pyTA error.
    return 'None'


if __name__ == '__main__':
    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod(verbose=True)

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['csv'],  # the names (strs) of imported modules
        'allowed-io': ['csv_to_list'],  # the names (strs) of functions that call print/open/input
        'max-line-length': 100,
        'disable': ['E1136']
    })
