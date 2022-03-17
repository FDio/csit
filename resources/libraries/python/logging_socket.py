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


class LoggingSocket:
    """This is a class for internal use (no Robot keywords are defined here).

    As sockets can be handled by a background thread,
    we just store instead of calling a real logger.
    """

    def __init__(self, under_socket, received=b""):
        """Store the given arguments.

        If under_socket is duck-detected to already be a LoggingSocket,
        its under_socket is re-used.

        :param under_socket: The underlying socket object.
        :param received: Last captured binary messages received.
        :type under_socket: socket.socket or compatible (can be LoggingSocket)
        :type sent: bytes
        """
        if hasattr(under_socket, u"under_socket"):
            under_socket = under_socket.under_socket
        self.under_socket = under_socket
        self.received = received

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
        self.under_socket.sendall(buffer)

    def recv_into(self, buffer, nbytes=0):
        """Receive a chunk of data, store to buffer, return length.

        This is where self.received is appended to.

        :param buffer: Read-write buffer to store the chunk into.
        :param nbytes: Read at most this many bytes (or all if 0).
        :type buffer: memoryview of bytearray or compatible
        :type nbytes: int
        :returns: The length of the chunk read.
        :rtype: int
        """
        n_received = self.under_socket.recv_into(buffer, nbytes)
        self.received += buffer[-n_received:]

    def flush_received(self):
        """Return and clean received.

        :returns: Received since last flush.
        :rtype: bytes
        """
        received = self.received
        self.received = b""
        return received
