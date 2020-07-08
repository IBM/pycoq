import pycoq.common
import pycoq.kernel
import os
import asyncio

async def printlines(aiter):
    async for line in aiter:
        print(line, end='')

async def main():

    cfg = pycoq.common.serapi_kernel()
    try:
        async with pycoq.kernel.LocalKernel(cfg) as serapi:

            await serapi.writeline('Quit')

            await printlines(serapi.readlines(timeout=1, quiet=True))
            await printlines(serapi.readlines_err(timeout=1, quiet=True))

    except FileNotFoundError as exc:
        print('failed to start serapi')
        
        



asyncio.run(main())

