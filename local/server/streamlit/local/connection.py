"""A Report Object which exposes a print method which can be used to
write objects out to a wbpage."""

from aiohttp import web, ClientSession
from aiohttp.client_exceptions import ClientConnectorError

import asyncio
import bson
import sys
import threading
import traceback

from streamlit.local.util import get_local_id
from streamlit.shared import config
from streamlit.shared.DeltaGenerator import DeltaGenerator
from streamlit.shared.ReportQueue import ReportQueue
from streamlit.shared.streamlit_msg_proto import new_report_msg

def _assert_singleton(method):
    """Asserts that this method is called on the singleton instance of
    Connection."""
    def inner(self, *args, **kwargs):
        assert self == Connection._connection, \
            f'Can only call {method.__name__}() on the singleton Connection.'
        return method(self, *args, **kwargs)
    inner.__name__ = method.__name__
    inner.__doc__ = method.__doc__
    return inner

def _assert_singleton_async(method):
    """Asserts that this coroutine is called on the singleton instance of
    Connection."""
    async def inner(self, *args, **kwargs):
        assert self == Connection._connection, \
            f'Can only call {method.__name__}() on the singleton Connection.'
        return await method(self, *args, **kwargs)
    inner.__name__ = method.__name__
    inner.__doc__ = method.__doc__
    return inner

def get_delta_generator():
    """Gets the DeltaGenerator for the singleton Connection instance,
    establishing that connection if necessary."""
    return Connection.get_connection().get_delta_generator()

class Connection:
    """This encapsulates a single connection the to the server for a single
    report."""

    # This is the singleton connection object.
    _connection = None

    def __init__(self):
        """
        Creates a new connection to the server.
        """
        # Create an ID for this Report
        self._report_id = bson.ObjectId()

        # Queue to store deltas as they flow across.
        self._queue = ReportQueue()

        # Set to false when the connection should close.
        self._is_open = True

        # This is the event loop to talk with the serverself.
        self._loop = asyncio.new_event_loop()

        # This is the class through which we can add elements to the Report
        self._delta_generator = DeltaGenerator(self._enqueue_delta)

    @classmethod
    def get_connection(cls):
        """Returns the singleton Connection object, instantiating one if
        necessary."""
        # Instantiate the singleton connection if necessary.
        if cls._connection == None:
            print('Instantiating the singleton connection.')
            # Create the new connection.
            cls._connection = Connection()
            cls._connection._connect_to_proxy()

            # When the current thread closes, then close down the connection.
            current_thread = threading.current_thread()
            def cleanup_on_exit():
                current_thread.join()
                print('The parent thread has closed. CLEANING UP')
                cls._connection._loop.call_soon_threadsafe(setattr,
                    cls._connection, '_is_open', False)
            threading.Thread(target=cleanup_on_exit, daemon=False).start()

        # Now that we're sure to have a connection, return it.
        return cls._connection

    @_assert_singleton
    def get_delta_generator(self):
        """Returns the DeltaGenerator for this report. This is the object
        that allows you to dispatch toplevel deltas to the Report, e.g.
        adding new elements."""
        return self._delta_generator

    @_assert_singleton
    def _enqueue_delta(self, delta):
        """Enqueues the given delta for transmission to the server."""
        self._loop.call_soon_threadsafe(self._queue, delta)

    @_assert_singleton
    def _connect_to_proxy(self):
        """Opens a connection to the server in a separate thread. Returns
        the event loop for that thread."""
        def connection_thread():
            self._loop.run_until_complete(self._attempt_connection())
            self._loop.close()
            print('Naturally closed the connection.')
            Connection._connection = None
        threading.Thread(target=connection_thread, daemon=False).start()

    @_assert_singleton_async
    async def _attempt_connection(self):
        """Tries to establish a connection to the proxy (launching the
        proxy if necessary). Then, pumps deltas through the connection."""
        # Create a connection URI.
        server = config.get_option('proxy.server')
        port = config.get_option('proxy.port')
        local_id = get_local_id()
        report_id = self._report_id
        uri = f'http://{server}:{port}/new/{local_id}/{report_id}'

        # Try to connect twice to the websocket
        session = ClientSession(loop=self._loop)
        try:
            # Try to connect to the proxy for the first time.
            try:
                async with session.ws_connect(uri) as ws:
                    await self._transmit_through_websocket(ws)
                    return
            except ClientConnectorError:
                pass

            # Connecting to the proxy failed, so let's start the proxy manually.
            await self._launch_proxy()

            # Try again to transmit data through the proxy
            try:
                async with session.ws_connect(uri) as ws:
                    await self._transmit_through_websocket(ws)
            except ClientConnectorError:
                print(f'Failed to attent to connect to {uri}.')

        finally:
            # Closing the session.
            await session.close()

    @_assert_singleton_async
    async def _launch_proxy(self):
        """Launches the proxy server."""
        wait_for_proxy_secs = config.get_option('local.waitForProxySecs')
        print('about to launch the proxy in a separate process', __file__)
        import os
        os.system('python -m streamlit.local.Proxy &')
        print('launched the proxy in a separate process.')
        print('sleeping while waiting for the proxy', wait_for_proxy_secs)
        await asyncio.sleep(wait_for_proxy_secs)
        print('Finished sleeping.')

    @_assert_singleton_async
    async def _transmit_through_websocket(self, ws):
        """Sends queue data across the websocket as it becomes available."""
        # Send the header information across.
        await new_report_msg(self._report_id, ws)

        # Send other information across.
        throttle_secs = config.get_option('local.throttleSecs')
        while self._is_open:
            await self._queue.flush_deltas(ws)
            await asyncio.sleep(throttle_secs)
        await self._queue.flush_deltas(ws)
