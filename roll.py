## The formatting for the roll command is
## @roll NdNN
## ex. @roll 2d6, @roll 1d4, @roll 5d20 etc


import os
import time
import re
import random
import sys
from slackclient import SlackClient

#bot's id as environment variable
BOT_ID = os.environ.get('BOT_ID')

#constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

#start Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

def roll(num, size):
    total = 0
    for i in range(0, num):
        total += random.randrange(1, size, 1)
    return total

def handle_command(command, channel):
    response = "I'm sorry human, I can't allow you to do that."
    dice = {"d2": 2, "d3": 3, "d4": 4, "d6": 6, "d10": 10, "d12": 12, "d20": 20, "d100": 100}
    num = 0
    n = re.compile('(\d*)d').findall(command)
    try:
        num = int(n[0])
        for k, v in dice.items():
            if k == command[1:]:
                response = roll(num, v)
                break
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
    except TypeError as e:
        print("Type Error: ", e)
    except NameError as n:
        print("Name Error: ", n)
    except:
        print("Error: ", sys.exc_info()[0])


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 s delay between reading
    random.seed(time.clock())
    if slack_client.rtm_connect():
        print("roll bot starting")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid token")

