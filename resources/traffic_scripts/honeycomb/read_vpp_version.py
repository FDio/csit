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
import threading
import argparse
from time import time

# Hello message with capabilities list for Netconf sessions.
hello = u"""
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="m-0">
<capabilities>
<capability>urn:ietf:params:netconf:base:1.0</capability>
</capabilities>
</hello>
]]>]]>"""

# RPC to retrieve VPP version (read performance, minimal processing in VPP)
get_version = u"""
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="m-1">
<get>
<filter xmlns:ns0="urn:ietf:params:xml:ns:netconf:base:1.0" ns0:type="subtree">
<vpp-state xmlns="urn:opendaylight:params:xml:ns:yang:vpp:management">
<version/>
</vpp-state>
</filter>
</get>
</rpc>
]]>]]>"""

# Number of threads to use
# Should match Honeycomb thread configuration for optimal performance
threads = 2
# Number of requests to make in each thread
requests = 50


class Counter(object):
    def __init__(self, start=0):
        self.lock = threading.Lock()
        self.value = start

    def increment(self, value=1):
        self.lock.acquire()
        val = self.value
        try:
            self.value += value
        finally:
            self.lock.release()
        return val


class timer(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def __enter__(self):
        self.start = time()
        return self

    def __exit__(self, *args):
        self.end = time()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        if self.verbose:
            print("elapsed time: %f ms" % self.msecs)


class ConfigBlaster(object):

    TIMEOUT = 10

    # Hello message with capabilities list for Netconf sessions.
    hello = u"""
    <hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="m-0">
    <capabilities>
    <capability>urn:ietf:params:netconf:base:1.0</capability>
    </capabilities>
    </hello>
    ]]>]]>"""

    # RPC to retrieve VPP version (minimal processing in VPP)
    request_template = u"""
    <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="m-1">
    <get>
    <filter xmlns:ns0="urn:ietf:params:xml:ns:netconf:base:1.0" ns0:type="subtree">
    <vpp-state xmlns="urn:opendaylight:params:xml:ns:yang:vpp:management">
    <version/>
    </vpp-state>
    </filter>
    </get>
    </rpc>
    ]]>]]>"""

    class FcbStats(object):
        """Stores and further processes statistics collected by worker
        threads during their execution.
        """

        def __init__(self):
            self.ok_rqst_rate = Counter(0.0)
            self.total_rqst_rate = Counter(0.0)
            self.ok_rqsts = Counter(0)
            self.total_rqsts = Counter(0)

        def process_stats(self, rqst_stats, elapsed_time):
            """Calculates the stats for request/reply throughput, and aggregates
            statistics across all threads.

            Args:
                rqst_stats: Request statistics dictionary
                elapsed_time: Elapsed time for the test

            Returns: Rates (requests/sec) for successfully finished requests
                     and the total number of requests.
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

        def get_ok_rqst_rate(self):
            return self.ok_rqst_rate.value

        def get_total_rqst_rate(self):
            return self.total_rqst_rate.value

        def get_ok_rqsts(self):
            return self.ok_rqsts.value

        def get_total_rqsts(self):
            return self.total_rqsts.value

    def __init__(self, host, port, ncycles, nthreads, nrequests):
        self.host = host
        self.port = port
        self.ncycles = ncycles
        self.nthreads = nthreads
        self.nrequests = nrequests

        self.stats = self.FcbStats()
        self.total_ok_rqsts = 0

        self.print_lock = threading.Lock()
        self.cond = threading.Condition()
        self.threads_done = 0

        self.recv_buf = 8192

    def send_request(self, sock):
        """Send Netconf request and receive the reply.
        :param sock: Socket object to use for transfer.
        :type sock: socket object

        :return: Response to request or error message.
        :rtype: str
        """

        sock.send(self.request_template)
        try:
            return sock.recv(self.recv_buf)
        except socket.timeout:
            return "timeout"
        except socket.error:
            return "error"

    def send_requests(self, tid):
        """
        Read entries from the Honeycomb operational data store. This function is
        executed by a worker thread. The number of entries created is determined
         by control parameters initialized when entryConfigBlaster is created.
        :param tid: Thread ID - used to id the Blaster thread when
        statistics for the thread are printed out
        :type tid: int
        :return: None
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
            print '    Thread {0}:\n        Sending {1} requests,'.format(
                tid, self.nrequests)

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
            print '\n    Thread %d results (ADD): ' % tid
            print '        Elapsed time: %.2fs,' % t.secs
            print '        Requests/s: %.2f OK, %.2f Total' % (
                ok_rps, total_rps)
            print '        Stats ({Requests}, {entries}): ',
            print rqst_stats,
            self.threads_done += 1

        sock.close()

        with self.cond:
            self.cond.notifyAll()

    def run_cycle(self, function):
        """Runs a test cycle. Each test consists of a
        <cycles> test cycles, where <threads> worker threads are
        started in each test cycle. Each thread reads <requests>
        entries using Netconf RPCs.
        :param function: Function to be executed.
        :type function: function
        :return: None
        """

        self.total_ok_rqsts = 0

        for c in range(self.ncycles):
            self.stats = self.FcbStats()
            with self.print_lock:
                print '\nCycle %d:' % c

            threads = []
            for i in range(self.nthreads):
                t = threading.Thread(target=function,
                                     args=(i,))
                threads.append(t)
                t.start()

            # Wait for all threads to finish and measure the execution time
            with timer() as t:
                for thread in threads:
                    thread.join()

            with self.print_lock:
                print '\n*** Test summary:'
                print '    Elapsed time:    {0}s'.format(t.secs)
                print '    Peak requests/s: {0} OK, {1} Total'.format(
                    self.stats.get_ok_rqst_rate(),
                    self.stats.get_total_rqst_rate())
                print '    Avg. requests/s: %.2f OK, %.2f Total (%.2f%% ' \
                      'of peak total)' % (
                    self.stats.get_ok_rqsts() / t.secs,
                    self.stats.get_total_rqsts() / t.secs,
                    (
                    self.stats.get_total_rqsts() / t.secs * 100) /
                    self.stats.get_total_rqst_rate())

                self.total_ok_rqsts += self.stats.get_ok_rqsts()
                self.threads_done = 0

    def add_blaster(self):
        self.run_cycle(self.send_requests)

    def get_ok_rqsts(self):
        return self.total_ok_rqsts


def create_arguments_parser():
    """Creates argument parser for test script.
    Shorthand to arg parser on library level in order to access and
    eventually enhance in ancestors.
    :return: argument parser supporting arguments and parameters
    """
    my_parser = argparse.ArgumentParser(
        description='entry reading performance test: Reads entries from '
                    'the config tree, as specified by optional parameters.')

    my_parser.add_argument('--host', default='127.0.0.1',
                           help='Host where odl controller is running ('
                                'default is 127.0.0.1).  '
                                'Specify a comma-separated list of hosts '
                                'to perform round-robin load-balancing.')
    my_parser.add_argument('--port', default=7777,
                           help='Port on which Honeycomb\'s Netconf is '
                                'listening (default is 7777 for TCP)')
    my_parser.add_argument('--cycles', type=int, default=1,
                           help='Number of entry read cycles; '
                                'default 1. <THREADS> worker '
                                'threads are started in each cycle and '
                                'the cycle '
                                'ends when all threads finish. Another '
                                'cycle is started when the previous cycle '
                                'finished.')
    my_parser.add_argument('--threads', type=int, default=1,
                           help='Number of request worker threads to '
                                'start in each cycle; default=1. '
                                'Each thread will read <entries> '
                                'entries.')
    my_parser.add_argument('--requests', type=int, default=10,
                           help='Number of requests that will be '
                                'made by each worker thread in '
                                'each cycle; '
                                'default 10')

    return my_parser

if __name__ == "__main__":

    parser = create_arguments_parser()
    in_args = parser.parse_args()

    fct = ConfigBlaster(in_args.host, in_args.port, in_args.cycles,
                        in_args.threads, in_args.requests)

    # Run through <cycles>, where <threads> are started in each cycle and
    # <entries> are added from each thread
    fct.add_blaster()

    print '    Successful reads:  %d\n' % fct.get_ok_rqsts()
