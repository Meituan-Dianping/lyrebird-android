import lyrebird
import pip
import time
import asyncio
from asyncio import Event
import threading


if __name__ == '__main__':
    pip.main(['install', '.',  '--upgrade'])
    lyrebird.debug()

    loop = asyncio.get_event_loop()
    loop.run_forever()
