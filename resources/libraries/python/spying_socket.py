# Copyright (c) 2020 Cisco and/or its affiliates.
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


class SpyingSocket:
    """This is a class for internal use (no Robot keywords are defined here).

    The intended use:
    1. Create and connect socket PAPI executor.
    2. Extract (and remember) the socket object from its transport.
    3. Create instance of this class (wrapping that object).
    4. Insert the instance to the transport (replacing the original socket).
    5. Perform two ordinary PAPI calls.
    6. Query this instance for the data needed.
    7. Feed newly created data directly to the remembered socket object.
    """

    def __init__(self, under_socket, sent=b"", received=b""):
        """Store the given arguments.

        If under_socket is detected to already be a SpyingSocket,
        its under_socket is re-used.

        :param under_socket: The underlying socket object.
        :param sent: Last binary message sent.
        :param received: Last binary message received.
        :type under_socket: socket.socket or compatible (can be SpyingSocket)
        :type sent: bytes
        :type received: bytes
        """
        if isinstance(under_socket, SpyingSocket):
            under_socket = under_socket.under_socket
        self.under_socket = under_socket
        """The underlying socket, most of calls just forward there."""
        self.sent = sent
        """Buffer of data sent. Appended on each chunk."""
        self.received = received
        """Buffer of data received. Appended on each chunk."""

    # TODO: __repr__, __str__?

    def fileno(self):
        """Return file descriptor so select works.

        :returns: File descriptor of the underlying socket.
        :rtype: int
        """
        return self.under_socket.fileno()

    def __eq__(self, other):
        """Permissive equality, so select started with under_socket works.

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
        self.under_socket.sendall(buffer)

    def recv_into(self, buffer, nbytes=0):
        """Receive a chunk of data, remember and store to buffer, return length.

        The implementation or remembering relies on readability after write.

        :param buffer: Read-write buffer to store the chunk into.
        :param nbytes: Read at most this mane bytes (or all if 0).
        :type buffer: memoryview of bytearray or compatible
        :type nbytes: int
        :returns: The length of the chunk read.
        :rtype: int
        """
        ret = self.under_socket.recv_into(buffer)
        self.received += buffer[:ret]
        return ret

    def flush_sent(self):
        """Return and clean sent.

        :returns: Sent since last flush.
        :rtype: bytes
        """
        sent = self.sent
        self.sent = b""
        return sent

    def flush_received(self):
        """Return and clean received.

        :returns: Received since last flush.
        :rtype: bytes
        """
        received = self.received
        self.received = b""
        return received
