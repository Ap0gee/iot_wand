import asyncio

async def poll():
    while 1:
        print('test')
        await asyncio.sleep(1)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    task = loop.create_task(poll())
    loop.run_until_complete(task)

    input()