from os import wait, write
import requests as req
import json
from bs4 import BeautifulSoup
import time

base_link = "https://hubble.figment.io/cosmos/chains"
base_figment = "https://hubble.figment.io"

def write_to_file(json_str):
    with open("votes.txt", "a") as f:
        f.write(json_str + "\n")
        f.close()

def get_votes(cosmo_hub_id, start_id = 1):
    # loop through each id until fail to get an id n times
    N = 5
    n_retries = N
    wait_time = 10 # 10 sec
    propose_id = start_id
    #push through option to push through failed-to-get proposal
    push_through = False

    while True:
        # status check
        if n_retries < 0 & (not push_through):
            break

        print("get votes of proposal {} in cosmohub-{} with retry = {} \n".format(propose_id, cosmo_hub_id, n_retries))

        # get data
        data_dir = "{}/cosmoshub-{}/governance/proposals/{}".format(base_link,cosmo_hub_id, propose_id)
        res = req.get(data_dir)

        # check res status code
            # invalid proposal --> exit crawler
        if res.status_code == 404:
            break

            # internal server error --> attempt N times to retrieve every 10 sec
        if res.status_code == 500:
            print("fail to retrieve proposal id={} \n".format(propose_id))
            n_retries -= 1
            time.sleep(wait_time)
            continue

        # handle data if successful (status code = 200)
        n_retries = N
        propose_id += 1

            # crawl data
        bs = BeautifulSoup(res.text, features="html.parser")
        table = bs.find("table", {"class": "table table-sm votes-table"})

            # check if data is missing
        table_children = table.findChildren("tr")
        if len(table_children) == 1:
            print("Data is missing at proposal {} in cosmos-hub{} \n".format(propose_id-1, cosmo_hub_id))
            continue

        for tr_item in table.findChildren("tr"):
            td_list = tr_item.findAll("td")
            user = dict()
            user["proposal"] = data_dir
            user["vote_option"] = td_list[0].getText()
            user["voter"] = base_figment + td_list[1].find("a")["href"]
            write_to_file(json.dumps(user))

if __name__ == "__main__":
    get_votes(1)
    get_votes(2)
    get_votes(3)