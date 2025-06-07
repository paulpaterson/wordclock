import sys
import json
import requests
import aiohttp
from omnilogic import OmniLogic
import time
import asyncio
import ssl
import click
import pprint
import datetime
import signal
import paramiko


async def get_pool_data(store):
    """Get data on the pool telemetry"""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    with aiohttp.TCPConnector(ssl=ssl_context) as conn:

        with open("../haywardlogin.py", "r") as f:
            text = f.read()
            vals = eval(text)
            username = vals['username']
            password = vals['password']

            omni = OmniLogic(username, password, aiohttp.ClientSession(connector=conn))
            status = await omni.get_telemetry_data()

    store['water'] = status[0]['BOWS'][0]['waterTemp']
    store['air'] = status[0]['airTemp']


def map_weather_name(name):
    """Return a simple version of the forecasted weather

    Returns either Sunny, Cloudy, Rainy

    """
    name = name.lower()
    if "sunny" in name or "clear" in name:
        return "Sunny"
    elif "cloud" in name or "fog" in name:
        return "Cloudy"
    elif "rain" in name or "shower" in name or "storm" in name:
        return "Rain"
    else:
        return name


def get_weather_forecast(store, hours):
    """Return the forecasted weather for the next few hours"""
    url = "https://api.weather.gov/gridpoints/HGX/31,80/forecast/hourly"
    response = requests.get(url)
    response.raise_for_status()
    forecast_data = response.json()
    look_ahead = []
    for period in forecast_data['properties']['periods']:
        forecast = period['shortForecast']
        usable_forecast = map_weather_name(forecast)
        look_ahead.append(usable_forecast)
    store['forecast'] = look_ahead[:hours]


def get_home_assistant(store):
    """Return data from home assistant"""
    client = paramiko.SSHClient()
    client.load_system_host_keys() # Load known hosts from your system
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #key = paramiko.RSAKey.("/Users/paul/.ssh/id_ed25519")# Auto add new hosts (be cautious in production)
    client.connect(
        hostname='homeassistant.local',
        port=22,
        username='paul',
        timeout=10
    )
    stdin, stdout, stderr = client.exec_command('cat /config/my_logs/data.txt')
    result = stdout.read()
    e = stderr.read()
    #print(str(result))
    #print(str(e))
    lines = result.splitlines()
    last_line = lines[-1]
    last_line = last_line.replace(b'True', b'true').replace(b'False', b'false')
    try:
        data = json.loads(last_line)
    except json.JSONDecodeError as err:
        print(f'Error decoding JSON from "{last_line}"')
        print(err)
        raise
    #print(data)
    store['water'] = data["Water"]
    store['air'] = data["Air"]
    store['upstairs-cooling'] = data["Upstairs-Cooling"]
    store['downstairs-cooling'] = data["Downstairs-Cooling"]
    client.close()


@click.command()
@click.option('--interval', type=int, default=5, help='How often to run (seconds)')
@click.option('--pool', is_flag=True, default=False, help='Whether to get pool information')
@click.option('--weather', is_flag=True, default=False, help='Whether to get weather information')
@click.option('--homeassistant', is_flag=True, default=False, help='Whether to get data from home assistant')
@click.option('--debug', is_flag=True, default=False, help='Drop into debug mode when complete')
@click.option('--iterations', type=int, default=-1, help='How many times to run')
@click.option('--forecast', type=int, default=16, help='How many hours of forecast to look ahead')
def main(interval, pool, weather, homeassistant, debug, iterations, forecast):
    store = {}
    try:
        while iterations:
            print(f'\n\nUpdating at {datetime.datetime.now()}\n')
            if pool:
                asyncio.run(get_pool_data(store))
            if weather:
                get_weather_forecast(store, forecast)
            if homeassistant:
                get_home_assistant(store)

            pprint.pprint(store)
            with open('local_data.json', 'w') as f:
                data = {
                    'update-time': datetime.datetime.now().isoformat(),
                    'pool-temp': int(store.get('water', -1)),
                    'air-temp': int(store.get('air', -1)),
                    'garage-open': False,
                    'ac-down-auto': True,
                    'ac-down-cool': store.get('downstairs-cooling', False),
                    'ac-up-cool': store.get('upstairs-cooling', False),
                    'ac-up-auto': True,
                    'forecast': store.get('forecast', [])
                }
                f.write(json.dumps(data, indent=4))
            #
            iterations -= 1
            if iterations:
                time.sleep(interval)
    except KeyboardInterrupt:
        print('CTRL-C detected. Stopping\n')
    #
    if debug:
        import pdb
        pdb.set_trace()


def signal_handler(sig, frame):
    """Handle the SIGTERM from SystemD"""
    print(f'Caught SIGTERM {sig}')
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)
    main()


