import json
import random
import requests
from bs4 import BeautifulSoup


def get_popular_numbers(tickets):
    popularity = {}

    for ticket in tickets:
        for number in ticket:
            popularity[number] = 1 if number not in popularity else popularity[number] + 1

    sorted_numbers = sorted(
        popularity.items(), key=lambda x: x[1], reverse=True)

    # create a list of unique numbers
    unique_numbers = list()
    for item, _ in sorted_numbers:
        if item in unique_numbers:
            continue
        unique_numbers.append(item)

    return unique_numbers


def split_tickets(tickets):
    return list(map(lambda x: x.text.strip().split(" - "), tickets))


def format_ticket(ticket):
    return "{} {} {} {} {} | {} {}".format(*ticket)


def get_statistical_ticket():
    url = "https://www.national-lottery.co.uk/results/euromillions/draw-history"

    source_code = requests.get(url)
    soup = BeautifulSoup(source_code.text, "lxml")

    main_numbers = split_tickets(soup.select(
        "li.table_cell_3 .table_cell_block"))
    popular_main_numbers = get_popular_numbers(main_numbers)

    lucky_numbers = split_tickets(soup.select(
        "li.table_cell_4 .table_cell_block"))
    popular_lucky_numbers = get_popular_numbers(lucky_numbers)

    ticket_to_play = popular_main_numbers[:5] + popular_lucky_numbers[:2]

    return list(map(int, ticket_to_play))


def get_random_ticket():
    return random.sample(range(1, 50), 5) + random.sample(range(1, 11), 2)


def get_fixed_ticket():
    try:
        with open("config.json") as json_data:
            data = json.load(json_data)
            if "fixed_ticket" not in data:
                raise Exception(
                    "Could not find a ticket under fixed_ticket key in config file")
            return data.get("fixed_ticket")

    except Exception as e:
        print(e)
        exit()


def generate_tickets(strategy="all"):
    if strategy == "statistical":
        return [get_statistical_ticket()]
    elif strategy == "random":
        return [get_random_ticket()]
    elif strategy == "fixed":
        return [get_fixed_ticket()]

    return [get_statistical_ticket(), get_random_ticket(), get_fixed_ticket()]


if __name__ == "__main__":
    tickets = generate_tickets()
    print("Today's tickets are:")

    for ticket in tickets:
        print(format_ticket(ticket))
