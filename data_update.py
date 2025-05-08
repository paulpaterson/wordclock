import json

import aiohttp
from omnilogic import OmniLogic
import time
import asyncio
import ssl
import click
import pprint


async def get_pool_data(store):
    """Get data on the pool telemetry"""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    conn = aiohttp.TCPConnector(ssl_context=ssl_context)

    with open("../haywardlogin.py", "r") as f:
        text = f.read()
        vals = eval(text)
        username = vals['username']
        password = vals['password']

    omni = OmniLogic(username, password, aiohttp.ClientSession(connector=conn))
    status = await omni.get_telemetry_data()
    store['water'] = status[0]['BOWS'][0]['waterTemp']
    store['air'] = status[0]['airTemp']


@click.command()
@click.option('--interval', type=int, default=5, help='How often to run (seconds)')
def main(interval):
    store = {}
    while True:
        asyncio.run(get_pool_data(store))
        print(store)
        with open('local_data.json', 'w') as f:
            data = {
                'pool-temp': int(store['water']),
                'air-temp': int(store['air']),
                'garage-open': False,
                'ac-down-auto': True,
                'ac-up-auto': True
            }
            f.write(json.dumps(data, indent=4))
        #
        time.sleep(interval)


if __name__ == "__main__":
    main()
