from __future__ import annotations

import asyncio
import logging

from xplonk.protocol import command, response


log = logging.getLogger(__name__)


class NNTP:
    """This is an implementation of the NNTP protocol as defined in RFC
       3977 most recently. It features a full disconnect between submitting
       events and actually retrieving the responses. This allows for queuing
       multiple commands and retrieving their responses as necessary.

       RFC 3977: https://tools.ietf.org/html/rfc3977"""

    _stream: None

    # While we are pipelining we will submit new commands from the submit
    # queue immediately, if we are not we will wait until the response queue
    # is empty before submitting new commands.
    _pipelining: bool

    _commands_pending: asyncio.Queue[command._Command]
    _responses_expected: asyncio.Queue[response._Response]
    _responses_pending: asyncio.Queue[response._Response]

    def __init__(self, stream: None) -> None:
        self._stream = None

        # After a connection the server MUST respond with a greeting to us
        # since our stream should be connected by the time we're here we will
        # expect that greeting.
        self._responses_expected = asyncio.Queue()
        self._responses_expected.put_nowait(response.GREETING())

        self._responses_pending = asyncio.Queue()
        self._commands_pending = asyncio.Queue()

        # We are not allowed to pipeline until after we receive our initial
        # greeting response.
        self._pipelining = False

    async def loop(self) -> None:
        """The main loop of an NNTP instance, this will take commands from the
           command queue and read them into the response queue."""

        while True:
            # If there's no commands to send and no responses to read then we
            # wait a bit.
            if (
                self._commands_pending.empty()
                and self._responses_expected.empty()
            ):
                await asyncio.sleep(0.1)
                continue

            # If we are pipelining we can submit new commands to the server, if
            # not then the expected responses queue needs to be empty before we
            # are allowed to submit new commands to the server.
            if not self._commands_pending.empty():
                if self._pipelining:
                    # submit command
                    pass
                else:
                    # don't submit command if there's still responses expected
                    pass

            if not self._responses_expected.empty():
                # XXX timeout + race?
                response_expected = await self._responses_expected.get()

                # Read the expected response from the stream
                response = await response_expected.from_stream(self._stream)
                await self._responses_pending.put(response)
