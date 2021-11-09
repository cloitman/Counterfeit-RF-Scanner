#!/usr/bin/python3

#
# Example code mostly from https://github.com/dougbrion/OctoRest
#

import json
from octorest import OctoRest

def make_client(url, apikey):
    try:
        client = OctoRest(url=url, apikey=apikey)
        return client
    except Exception as e:
        print(e)

def get_version():
    client = make_client()
    message = "You are using OctoPrint v" + client.version['server'] + "\n"
    return message

def get_printer_info(url, apikey):
    try:
        client = make_client(url, apikey)
        # client = OctoRest(url="http://octopi.local", apikey="YouShallNotPass")
        message = ""
        message += str(client.version) + "\n"
        message += str(client.job_info()) + "\n"
        printing = client.printer()['state']['flags']['printing']
        if printing:
            message += "Currently printing!\n"
        else:
            message += "Not currently printing...\n"
        return message
    except Exception as e:
        print(e)

def main(url, apikey):
    c = make_client()
    for k in c.files()['files']:
        print(k['name'])

if __name__ == "__main__":

    # Read url and apikey from settings.json file provided by user
    with open("settings.json", "r") as read_file:
        data = json.load(read_file)

    url    = data['url']
    apikey = data['apikey']

    # Get printer info
    print( get_printer_info(url, apikey) )

