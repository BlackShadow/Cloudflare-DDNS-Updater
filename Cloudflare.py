import os
import sys
import requests
import json
import time
from configparser import ConfigParser
from sys import exit


def read_settings():
    config = ConfigParser()

    # Get the script's directory, considering PyInstaller and regular script execution
    script_directory = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    settings_file_path = os.path.join(script_directory, 'settings.ini')

    if not config.read(settings_file_path):
        create_default_settings(config, settings_file_path)

    api_key = config.get('Cloudflare', 'api_key')
    zone_id = config.get('Cloudflare', 'zone_id')
    email = config.get('Cloudflare', 'email')
    domain = config.get('Domain', 'name')

    return api_key, zone_id, email, domain

def create_default_settings(config, settings_file_path):
    config['Cloudflare'] = {
        'api_key': 'your_global_api_key',
        'zone_id': 'your_zone_id',
        'email': 'your_email@example.com'
    }

    config['Domain'] = {
        'name': 'your_domain'
    }

    with open(settings_file_path, 'w') as config_file:
        config.write(config_file)

    print("Settings.ini is missing. Creating a new settings file. Script exiting now...")

    # Add a delay of 5 seconds
    time.sleep(5)

    exit()

# Cloudflare API details
api_key, zone_id, email, domain = read_settings()

# Cloudflare API endpoint URLs
base_url = 'https://api.cloudflare.com/client/v4/'
dns_records_url = f'{base_url}zones/{zone_id}/dns_records'

headers = {
    'X-Auth-Email': email,
    'X-Auth-Key': api_key,
    'Content-Type': 'application/json'
}

def get_current_ip():
    # Function to get your current public IP address
    response = requests.get('https://api64.ipify.org?format=json')
    return response.json()['ip']

def get_record_id():
    # Function to get the record ID based on the domain name
    params = {
        'type': 'A',
        'name': domain,
        'page': 1,
        'per_page': 1
    }

    try:
        response = requests.get(dns_records_url, headers=headers, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx status codes)

        response_json = response.json()

        if 'result' in response_json and len(response_json['result']) > 0:
            return response_json['result'][0]['id']
        else:
            time.sleep(5)
            print(f'Error getting record ID. Response: {response_json}')
            return None

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            print("ERROR: Cloudflare cridentals are either wrong or missing. Check settings.ini and make sure you have entered correct details.")
            time.sleep(6)
            exit()
        else:
            print(f'HTTP error occurred: {http_err}')
            exit()

    except requests.exceptions.RequestException as req_err:
        print(f'Error in the Cloudflare API request: {req_err}')
        time.sleep(5)
        exit()

def get_record_ip(record_id):
    # Function to get the current IP address from Cloudflare
    response = requests.get(f'{dns_records_url}/{record_id}', headers=headers)
    response_json = response.json()

    if 'result' in response_json and 'content' in response_json['result']:
        return response_json['result']['content']
    else:
        print(f'Error getting record IP. Response: {response_json}')
        return None

def update_record_ip(record_id, new_ip):
    # Function to update the A record IP address in Cloudflare
    data = {
        'type': 'A',
        'name': domain,
        'content': new_ip,
        'ttl': 120,
        'proxied': False
    }
    response = requests.put(f'{dns_records_url}/{record_id}', headers=headers, data=json.dumps(data))
    return response.json()

def main():
    while True:
        try:
            record_id = get_record_id()

            if record_id is not None:
                current_ip = get_current_ip()
                record_ip = get_record_ip(record_id)

                if record_ip is not None:
                    if current_ip == record_ip:
                        print(f'STATUS: No IP change detected. Next check in 15 minutes.')
                    else:
                        update_response = update_record_ip(record_id, current_ip)

                        if 'success' in update_response and update_response['success']:
                            print(f'STATUS: IP change detected! IP address updated to {current_ip}. Next check in 15 minutes.')
                        else:
                            print(f'Error updating IP. Response: {update_response}')

            time.sleep(900)  # Sleep for 15 minutes before checking again

        except Exception as e:
            print(f'An error occurred: {e}')
            time.sleep(900)  # Sleep for 15 minutes before retrying

if __name__ == "__main__":
    main()
