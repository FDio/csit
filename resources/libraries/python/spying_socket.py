# Copyright (c) 2022 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Class for manipulating PAPI sockets."""

from robot.api import logger


class SpyingSocket:
    """This is a class for internal use (no Robot keywords are defined here).

    The intended use:
    1. Create and connect socket PAPI executor.
    2. Extract the socket object from its transport.
    3. Create instance of this class (wrapping that object).
    4. Insert the new instance to the transport (replacing the original socket).
    5. Perform two ordinary PAPI calls.
    6. Query this instance for the data needed by bytes_template.
    7. Restore the original socket object in transport (or use under_socket).
    8. Feed newly created data directly to the restored socket object.
    """

    def __init__(self, under_socket, capture=False, log=True, sent=b""):
        """Store the given arguments.

        If under_socket is detected to already be a SpyingSocket,
        its under_socket is re-used.

        The received data is not spied on,
        as vpp_instance.transport.q.get(True, timeout),
        or even vpp_instance.transport._read() retrieves raw data
        already nicely packaged into a single messages.

        After initial messages are captured, it is recommended
        to swap back under_socket to transport, to avoid call overhead.
        Or the original socket. The difference is only if it was SpyingSocket
        already, and you want to resume spying on that.

        :param under_socket: The underlying socket object.
        :param capture: Whether the data sent should be remembered.
        :param sent: Last captured binary message sent.
        :type under_socket: socket.socket or compatible (can be SpyingSocket)
        :type capture: bool
        :type sent: bytes
        """
        if isinstance(under_socket, SpyingSocket):
            under_socket = under_socket.under_socket
        self.under_socket = under_socket
        self.capture = capture
        self.log = log
        self.sent = sent

    # TODO: __repr__, __str__?

    def fileno(self):
        """Return file descriptor, so select() works.

        :returns: File descriptor of the underlying socket.
        :rtype: int
        """
        return self.under_socket.fileno()

    def __eq__(self, other):
        """Permissive equality, so select started with under_socket works.

        This also handles situations where under_socket is swapped back.

        :param other: Other socket to compare to.
        :type other: socket.socket or SpyingSocket
        :returns: Whether the fileno() is the same.
        :rtype: bool
        """
        # TODO: Do we care to raise NotImplemented on unrelated types?
        return self.fileno() == other.fileno()

    def close(self):
        """Close the underlying socket.

        :raises OSError: As thrown from underlying socket.
        """
        return self.under_socket.close()

    def sendall(self, buffer):
        """Send all data from buffer to socket, remember (copy of) the buffer.

        :param buffer: The data to send.
        :type buffer: bytes or compatible
        """
        self.sent += bytes(buffer)

    def send(self, buffer):
        """Send (maybe not all) data from buffer to socket, remember data sent.

        Older VPP builds are using send instead of sendall.
        TODO: How much older? Can we stop supporting already?

        :param buffer: The data to send.
        :type buffer: bytes or compatible
        :returns: Number of bytes sent.
        :rtype: int
        """
        buffer_copy = bytes(buffer)
        self.sent += buffer_copy
        return len(buffer_copy)

    def recv_into(self, buffer, nbytes=0):
        """Receive a chunk of data, store to buffer, return length.

        Just a pass-through call.

        :param buffer: Read-write buffer to store the chunk into.
        :param nbytes: Read at most this many bytes (or all if 0).
        :type buffer: memoryview of bytearray or compatible
        :type nbytes: int
        :returns: The length of the chunk read.
        :rtype: int
        """
        return self.under_socket.recv_into(buffer, nbytes)

    def flush(self):
        """Return and clean sent.

        :returns: Sent since last flush.
        :rtype: bytes
        """
        if self.log:
            logger.trace(u"flush starts,")
            logger.console(u"flush starts,")
        self.under_socket.sendall(self.sent)
        if self.log:
            logger.trace(f"flushed: {buffer.hex()}")
            logger.console(f"flushed: {buffer.hex()}")
        self.sent = b""
