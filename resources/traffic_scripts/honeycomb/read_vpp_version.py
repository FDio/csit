# Copyright (c) 2017 Cisco and/or its affiliates.
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

import socket
import multiprocessing
import argparse
from time import time


class Counter(object):
    """Counter used for stats collection."""
    def __init__(self, start=0):
        """Initializer."""
        self.lock = multiprocessing.Lock()
        self.value = start

    def increment(self, value=1):
        """Increment counter and return the new value."""
        self.lock.acquire()
        val = self.value
        try:
            self.value += value
        finally:
            self.lock.release()
        return val


class timer(object):
    """Timer used used during test execution."""
    def __init__(self, verbose=False):
        self.verbose = verbose

    def __enter__(self):
        """Start the timer."""
        self.start = time()
        return self

    def __exit__(self, *args):
        """Stop the timer and save current value."""
        self.end = time()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        if self.verbose:
            print("elapsed time: {0} ms".format(self.msecs))


class ConfigBlaster(object):
    """Generates Netconf requests, receives replies and collects statistics."""

    TIMEOUT = 10

    # Hello message with capabilities list for Netconf sessions.
    hello = u"""<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"
    message-id="m-0">
    <capabilities>
    <capability>urn:ietf:params:netconf:base:1.0</capability>
    </capabilities>
    </hello>
    ]]>]]>"""

    # RPC to retrieve VPP version (minimal processing in VPP)
    request_template = u"""<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"
    message-id="m-1">
    <get>
    <filter xmlns:ns0="urn:ietf:params:xml:ns:netconf:base:1.0"
    ns0:type="subtree">
    <vpp-state xmlns="urn:opendaylight:params:xml:ns:yang:vpp:management">
    <version/>
    </vpp-state>
    </filter>
    </get>
    </rpc>
    ]]>]]>"""

    class Stats(object):
        """Stores and further processes statistics collected by worker
        threads during their execution.
        """

        def __init__(self):
            """Initializer."""
            self.ok_rqst_rate = Counter(0)
            self.total_rqst_rate = Counter(0)
            self.ok_rqsts = Counter(0)
            self.total_rqsts = Counter(0)

        def process_stats(self, rqst_stats, elapsed_time):
            """Calculates the stats for request/reply throughput, and aggregates
            statistics across all threads.

            :param rqst_stats: Request statistics dictionary.
            :param elapsed_time: Elapsed time for the test.
            :type rqst_stats: dict
            :type elapsed_time: int
            :returns: Rates (requests/sec) for successfully finished requests
                     and the total number of requests.
            :rtype: tuple
            """
            ok_rqsts = rqst_stats["OK"]
            total_rqsts = sum(rqst_stats.values())

            ok_rqst_rate = ok_rqsts / elapsed_time
            total_rqst_rate = total_rqsts / elapsed_time

            self.ok_rqsts.increment(ok_rqsts)
            self.total_rqsts.increment(total_rqsts)

            self.ok_rqst_rate.increment(ok_rqst_rate)
            self.total_rqst_rate.increment(total_rqst_rate)

            return ok_rqst_rate, total_rqst_rate

        @property
        def get_ok_rqst_rate(self):
            return self.ok_rqst_rate.value

        @property
        def get_total_rqst_rate(self):
            return self.total_rqst_rate.value

        @property
        def get_ok_rqsts(self):
            return self.ok_rqsts.value

        @property
        def get_total_rqsts(self):
            return self.total_rqsts.value

    def __init__(self, host, port, ncycles, nthreads, nrequests):
        """Initializer.

        :param host: Target IP address.
        :param port: Target port.
        :param ncycles: Number of test cycles.
        :param nthreads: Number of threads for packet generation.
        :param nrequests: Number of requests to send per thread.
        :type host: str
        :type port: int
        :type ncycles: int
        :type nthreads: int
        :type nrequests: int
        """

        self.host = host
        self.port = port
        self.ncycles = ncycles
        self.nthreads = nthreads
        self.nrequests = nrequests

        self.stats = self.Stats()
        self.total_ok_rqsts = 0

        self.print_lock = multiprocessing.Lock()
        self.cond = multiprocessing.Condition()
        self.threads_done = 0

        self.recv_buf = 8192

    def send_request(self, sock):
        """Send Netconf request and receive the reply.

        :param sock: Socket object to use for transfer.
        :type sock: socket object
        :returns: Response to request or error message.
        :rtype: str
        """

        sock.send(self.request_template)
        try:
            return sock.recv(self.recv_buf)
        except socket.timeout:
            return "timeout"
        except socket.error:
            return "error"

    def send_requests(self, tid, stats):
        """Read entries from the Honeycomb operational data store. This function
        is executed by a worker thread.

        :param tid: Thread ID - used to id the Blaster thread when
        statistics for the thread are printed out.
        :param stats: Synchronized queue object for returning execution stats.
        :type tid: int
        :type stats: multiprocessing.Queue
        """

        rqst_stats = {"OK": 0, "Error": 0, "Timeout": 0}

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        # Initiate connection
        sock.connect((self.host, self.port))
        # Send hello message
        sock.send(self.hello)
        # Receive hello message
        sock.recv(self.recv_buf)
        # Determine length of expected responses
        self.recv_buf = len(self.send_request(sock))

        with self.print_lock:
            print("\n    Thread {0}:\n"
                  "        Sending {1} requests".format(tid,
                                                        self.nrequests))

        replies = [None]*self.nrequests
        with timer() as t:
            for x in range(self.nrequests):
                sts = self.send_request(sock)
                replies[x] = sts

        for reply in replies:
            if reply == "timeout":
                rqst_stats["Timeout"] += 1
            elif "error" in reply:
                rqst_stats["Error"] += 1
            else:
                rqst_stats["OK"] += 1

        ok_rps, total_rps = self.stats.process_stats(
            rqst_stats, t.secs)

        with self.print_lock:
            print("\n    Thread {0} results (READ): ".format(tid))
            print("        Elapsed time: {0:.2f}s,".format(t.secs))
            print("        Requests/s: {0:.2f} OK, {1:.2f} Total".format(
                ok_rps, total_rps))
            print("        Stats ({Requests}, {entries}): "),
            print(rqst_stats)
            self.threads_done += 1

        sock.close()

        stats.put({"stats": rqst_stats, "time": t.secs})

        with self.cond:
            self.cond.notify_all()

    def run_cycle(self, function):
        """Runs a test cycle. Each test consists of <cycles> test cycles, where
        <threads> worker threads are started in each test cycle. Each thread
        reads <requests> entries using Netconf RPCs.

        :param function: Function to be executed in each thread.
        :type function: function
        """

        self.total_ok_rqsts = 0
        stats_queue = multiprocessing.Queue()

        for c in range(self.ncycles):
            self.stats = self.Stats()
            with self.print_lock:
                print "\nCycle {0}:".format(c)

            threads = []
            thread_stats = []
            for i in range(self.nthreads):
                t = multiprocessing.Process(target=function,
                                            args=(i, stats_queue))
                threads.append(t)
                t.start()

            # Wait for all threads to finish and measure the execution time
            with timer() as t:
                for _ in threads:
                    thread_stats.append(stats_queue.get())
                for thread in threads:
                    thread.join()

            for item in thread_stats:
                self.stats.process_stats(item["stats"], item["time"])

            with self.print_lock:
                print("\n*** Test summary:")
                print("    Elapsed time:    {0:.2f}s".format(t.secs))
                print(
                    "    Peak requests/s: {0:.2f} OK, {1:.2f} Total".format(
                        self.stats.get_ok_rqst_rate,
                        self.stats.get_total_rqst_rate))
                print(
                    "    Avg. requests/s: {0:.2f} OK, {1:.2f} Total ({2:.2f} "
                    "of peak total)".format(
                        self.stats.get_ok_rqsts / t.secs,
                        self.stats.get_total_rqsts / t.secs,
                        (self.stats.get_total_rqsts / t.secs * 100) /
                        self.stats.get_total_rqst_rate))

            self.total_ok_rqsts += self.stats.get_ok_rqsts

            self.threads_done = 0

    def add_blaster(self):
        """Run the test."""
        self.run_cycle(self.send_requests)

    @property
    def get_ok_rqsts(self):
        return self.total_ok_rqsts


def create_arguments_parser():
    """Creates argument parser for test script.
    Shorthand to arg parser on library level in order to access and
    eventually enhance in ancestors.

    :returns: argument parser supporting arguments and parameters
    :rtype: argparse.ArgumentParser
    """
    my_parser = argparse.ArgumentParser(
        description="entry reading performance test: Reads entries from "
                    "the config tree, as specified by optional parameters.")

    my_parser.add_argument(
        "--host", default="127.0.0.1",
        help="Host where odl controller is running (default is 127.0.0.1).")
    my_parser.add_argument(
        "--port", default=7777,
        help="Port on which Honeycomb's Netconf is listening"
             " (default is 7777 for TCP)")
    my_parser.add_argument(
        "--cycles", type=int, default=1,
        help="Number of entry read cycles; default 1. <THREADS> worker threads "
             "are started in each cycle and the cycle ends when all threads "
             "finish. Another cycle is started when the previous cycle "
             "is finished.")
    my_parser.add_argument(
        "--threads", type=int, default=1,
        help="Number of request worker threads to start in each cycle; "
             "default=1. Each thread will read <entries> entries.")
    my_parser.add_argument(
        "--requests", type=int, default=10,
        help="Number of requests that will be made by each worker thread "
             "in each cycle; default 10")

    return my_parser

if __name__ == "__main__":

    parser = create_arguments_parser()
    in_args = parser.parse_args()

    fct = ConfigBlaster(in_args.host, in_args.port, in_args.cycles,
                        in_args.threads, in_args.requests)

    # Run through <cycles>, where <threads> are started in each cycle and
    # <entries> are added from each thread
    fct.add_blaster()

    print "    Successful reads:  {0}\n".format(fct.get_ok_rqsts)
