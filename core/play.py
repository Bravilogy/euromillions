import json
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from core.tickets_generator import generate_tickets, format_ticket


def delayed_message(pre_run_message=None, post_run_message=None):
    def decorator(f):
        def wrapper(*args, **kargs):
            time.sleep(.5)

            if pre_run_message:
                print(pre_run_message)

            result = f(*args, **kargs)

            if post_run_message:
                print(post_run_message)

            return result
        return wrapper
    return decorator


@delayed_message("Calculating the next play day")
def get_next_play_day():
    today = datetime.today().weekday()
    return "FRIDAY" if 1 < today <= 4 else "TUESDAY"


@delayed_message("Fetching synchronizer data")
def get_synchronizer_data(session):
    response = session.get("https://www.national-lottery.co.uk/sign-in")

    soup = BeautifulSoup(response.text, "lxml")

    return {"SYNCHRONIZER_TOKEN": soup.find(id="SYNCHRONIZER_TOKEN")["value"],
            "SYNCHRONIZER_URI": soup.find(id="SYNCHRONIZER_URI")["value"]}


@delayed_message("Trying to log in to the account")
def login(client):
    url = "https://www.national-lottery.co.uk/login/authenticate"
    data, session = client.config, client.session

    required_fields = ["username", "password",
                       "SYNCHRONIZER_TOKEN", "SYNCHRONIZER_URI"]

    payload = {k: v for k, v in data.items() if k in required_fields}

    response = session.post(url, data=payload)

    if "Please check your details" in response.text or "Sign out" not in response.text:
        raise Exception("Could not log in to the account")


@delayed_message("Fetching the play ID")
def get_play_id(session):
    url = "https://www.national-lottery.co.uk/games/euromillions"
    source_code = session.get(url).content

    soup = BeautifulSoup(source_code, "lxml")
    play_id = soup.find(id="playId")["value"]

    if "play" not in play_id:
        raise Exception("Could not fetch the playId")

    return play_id


@delayed_message("Creating a play slip", "Play slip created successfully")
def create_play_slip(client, tickets):
    url = "https://www.national-lottery.co.uk/games/euromillions/create-play-slip"
    session, data = client.session, client.config

    headers = {
        "upgrade-insecure-requests": "1",
        "referer": "https://www.national-lottery.co.uk/games/euromillions?icid=-:mm:-:mdg:em:dbg:pl:co",
        "user-agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; .NET CLR 1.1.4322)",
        "host": "www.national-lottery.co.uk",
        "content-type": "application/x-www-form-urlencoded",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    play_slip_data = {
        "playId": data["play_id"],
        "_drawDays": "",
        "drawDays": get_next_play_day(),
        "numberWeeks": data["number_weeks"] if "number_weeks" in data else 1
    }

    for ticket_index, ticket in enumerate(tickets):
        col_index = 0

        for number_index, number in enumerate(ticket):
            if number_index == 5:
                col_index = 0

            data_index = "line_{}_pool_{}_col_{}".format(
                ticket_index, 0 if number_index <= 4 else 1, col_index)
            play_slip_data[data_index] = number

            col_index += 1

    # create a play slip
    session.post(url, data=play_slip_data, headers=headers)

    # check if the play slip has been created and is waiting to be confirmed
    url = "https://www.national-lottery.co.uk/games/euromillions/confirm-play-slip"
    response = session.get(url, params={"playId": data["play_id"]})

    if "Check your play slip" not in response.text:
        raise Exception("Could not create a play slip")


@delayed_message("Confirming tickets", "All done!")
def confirm_play_slip(client):
    url = "https://www.national-lottery.co.uk/games/euromillions/confirm-play-slip"
    session, data = client.session, client.config

    headers = {
        "upgrade-insecure-requests": "1",
        "referer": "https://www.national-lottery.co.uk/games/euromillions/confirm-play-slip?playId={}".format(
            data["play_id"]),
        "user-agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; .NET CLR 1.1.4322)",
        "host": "www.national-lottery.co.uk",
        "origin": "https://www.national-lottery.co.uk",
        "content-type": "application/x-www-form-urlencoded",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    sync_data = {
        "confirm": "Buy now",
        "SYNCHRONIZER_TOKEN": data["SYNCHRONIZER_TOKEN"],
        "SYNCHRONIZER_URI": data["SYNCHRONIZER_URI"]
    }

    params = {"playId": data["play_id"], "isAfterRegistration": ""}

    response = session.post(
        url, params=params, data=sync_data, headers=headers)

    if "Good luck!" not in response.text:
        raise Exception("Could not buy tickets. {}".format(
            "Not enough funds" if "Step 1 - Add funds" in response.text else ""))


class Client:
    def __init__(self, config):
        self.config = config

        required_fields = ["username", "password"]
        for field in required_fields:
            if field not in self.config:
                raise ValueError(
                    "Could not find the {} field in config file".format(field))

        self.session = requests.Session()
        self.config.update(get_synchronizer_data(self.session))
        self.config.update({"play_id": get_play_id(self.session)})


def play():
    try:
        with open("config.json") as config_data:
            config = json.load(config_data)

            print("Creating a session")
            client = Client(config)

            login(client)

            tickets = generate_tickets(
                config["strategy"] if "strategy" in config else "statistical")

            print("Tickets we will be playing:")
            for ticket in tickets:
                print(format_ticket(ticket))

            create_play_slip(client, tickets)

            confirm_play_slip(client)

    except Exception as e:
        print(e)
        exit()
