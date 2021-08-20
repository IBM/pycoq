import asyncio
import dataclasses
import time
from typing import Union

from pycoq.common import LocalKernelConfig, RemoteKernelConfig
from pycoq.common import TIMEOUT_TERMINATE

import pycoq.log

KernelConfig = Union[LocalKernelConfig, RemoteKernelConfig]

PIPE_BUFFER_LIMIT = 2048*1024*1024  # 2048 Mb

async def readline(stream, timeout=None) -> str: 
    """ reads line from stream 
    raises asyncio.TimeoutError if timeout is exceeded
    """

    line = await asyncio.wait_for(stream.readline(), timeout=timeout)
    return line.decode()

async def readlines(stream, count=None, timeout=None, quiet=True):
    """ yields upto count lines from stream 
    if quiet then stops yielding when timeout is exceeded 
    otherwise raise asyncio.TimeoutError
    """
    i = 0 
    while (count is None) or i < count:
        try:
            line = await readline(stream, timeout)
            if not line:
                break
        except asyncio.TimeoutError:
            if not quiet:
                raise asyncio.TimeoutError
            break
        i += 1
        yield line

class LocalKernel():
    """ implements interface readline, readlines, writeline to a local kernel

    """
    def __init__(self, cfg: LocalKernelConfig):
        self.cfg = cfg
        self._proc = None
        self._reader = None
        self._reader_err = None
        self._writer = None

    async def __aexit__(self, exception_type, exception_value, traceback):
        await self.terminate(timeout=TIMEOUT_TERMINATE)
            
    async def start(self):
        cfg = self.cfg
        cmd = cfg.command
        env = cfg.env
        cwd = cfg.pwd
        self._proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
            env=env,
            cwd=cwd,
            limit=PIPE_BUFFER_LIMIT,
            )
        self._reader = self._proc.stdout
        self._reader_err = self._proc.stderr
        self._writer = self._proc.stdin
        pycoq.log.info(f"process with {self._proc.pid} started as")
        pycoq.log.info(f"cmd: {cmd}")
        pycoq.log.info(f"cwd: {cwd}")


    async def __aenter__(self):
        """ starts local kernel
        """
        await self.start()
        return self
    
        
        
    async def readline(self, timeout=None) -> str:
        """ reads line from kernel stdout """
        line = await readline(self._reader, timeout)
        return line


    async def readline_err(self, timeout=None) -> str:
        """ reads line from kernel stderr """
        line = await readline(self._reader_err, timeout)
        return line

    async def readlines(self, count=None, timeout=None, quiet=True) -> str:
        """ reads lines from kernel stdout
        the options are as in kernel.readlines()
        """
        async for line in readlines(self._reader, count, timeout, quiet):
            yield line
        

    async def readlines_err(self, count=None, timeout=None, quiet=True) -> str:
        """ reads lines from kernel stderr
        the options are as in kernel.readlines()
        """
        async for line in readlines(self._reader_err, count, timeout, quiet):
            yield line

        
    async def write(self, data):
        """ writes data to kernel input """
        bdata = data.encode()
        self._writer.write(bdata)
        await self._writer.drain()


    async def writeline(self, line):
        """ writes line to kernel input """
        data = line + '\n'
        await self.write(data)


    async def _nice_terminate(self, timeout=None):
        self._writer.write_eof()
        await self._writer.wait_closed()
        await self._proc.wait()


    async def terminate(self, timeout=None):
        """ closes local kernel process """
        
        try:
            await asyncio.wait_for(self._nice_terminate(), timeout=timeout)
        except (asyncio.TimeoutError, BrokenPipeError, ConnectionResetError):
            try:
                self._proc.terminate()
                await asyncio.wait_for(self._proc.wait(), timeout=timeout)
            except  asyncio.TimeoutError:
                try:
                    self._proc.kill()
                    await asyncio.wait_for(self._proc.wait(), timeout=timeout)
                except asyncio.TimeoutError:
                    raise TimeoutError(f"LocalKernel.terminate() did not succeed with timeout={timeout}")
                except ProcessLookupError:
                    pass
            except ProcessLookupError:
                pass
