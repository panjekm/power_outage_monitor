import sys
from datetime import datetime
import time
import argparse
import requests
import config
import ntplib

parser = argparse.ArgumentParser()
parser.add_argument("--boot", help="Assume this script was just started on a fresh boot",
                    action="store_true")
args = parser.parse_args()

heartbeat_filename = '/home/panjekm/codebase/power_outage_monitor/data/heartbeat.txt'
boot_history_filename = '/home/panjekm/codebase/power_outage_monitor/data/boot_history.txt'

if args.boot:
    print("Just Booted! Checking downtime...")
    input_file = open(heartbeat_filename, "r")
    heartbeat_date_time = datetime.strptime(input_file.read(), '%d/%m/%Y %H:%M:%S')
    input_file.close()

    boot_time_start = datetime.now()

    # Make sure the current time is correct.
    while True:
        try:
            ntp_client = ntplib.NTPClient()
            response = ntp_client.request('pool.ntp.org', version=3)
            ntp_time_now = datetime.fromtimestamp(response.tx_time)
            break
        except Exception as e:
            print("NTP threw an exception! Retrying...")
            time.sleep(60)

    boot_time_delay = datetime.now() - boot_time_start

    # Determine the number of days, hours, minutes, and seconds the system was down for
    time_delta = ntp_time_now - heartbeat_date_time - boot_time_delay
    days = time_delta.days
    seconds = time_delta.seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Format the days, hours, minutes, and seconds for display
    system_down_time = ""
    if (days != 0):
        system_down_time += str(days) + "days, "
    if (hours != 0 or system_down_time != ""):
        system_down_time += str(hours) + "hours, "
    if (minutes != 0 or system_down_time != ""):
        system_down_time += str(minutes) + "minutes, "
    system_down_time += str(seconds) + "seconds."
    if days == 0 and hours == 0:
        system_down_time = system_down_time.replace(",", "")
    
    print("System was down for: ", system_down_time)

    # Log last heartbeat and next boot time.
    output_file = open(boot_history_filename, "a")
    log = "Boot: " + datetime.now().strftime('%d/%m/%Y %H:%M:%S') + "\t Last heartbeat: " + heartbeat_date_time.strftime('%d/%m/%Y %H:%M:%S') + "\t Diff: " + system_down_time + "\n"
    output_file.write(log)
    output_file.close()

    # Inform user via Telegram.
    try:
        telegram_msg = "[Power Outage Monitoring]: Power was restored in SG, downtime was: " + system_down_time
        telegram_url = f'https://api.telegram.org/bot{config.telegram_token}/sendMessage'
        response = requests.post(telegram_url, json={'chat_id': config.telegram_chat_id, 'text': telegram_msg})
        print(response.text)
    except Exception as e:
        print(e)

while True:
    # Get and format the current date and time
    current_date_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    # Write the "heartbeat" to a file
    output_file = open(heartbeat_filename, "w")
    output_file.write(current_date_time)
    output_file.close()
    # print("Heartbeat updated:",current_date_time)
    time.sleep(10)