import aiohttp
from omnilogic import OmniLogic
import time
import asyncio
import ssl

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

if __name__ == "__main__":
    store = {}
    while True:
        asyncio.run(get_pool_data(store))
        print(store)
        with open('local_data.json', 'w') as f:
            f.write('{\n')
            f.write(f'"pool-temp": {store["water"]},\n')
            f.write(f'"air-temp": {store["air"]},\n')
            f.write('"garage-open": false, "ac-down-auto": true, "ac-up-auto": true }')
        #
        time.sleep(10*60)

