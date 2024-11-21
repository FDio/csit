"""
--------------------------------------------------------------------------------

This module provide functions to "de-compress" JSON file specifying a traffic
profile for TRex.

=============
 JSON Format
=============

The input and generated JSON files are not prettyfied, so:
- no intendation,
- no whitespaces,
- delimiters: ',' and ':' not ', ' nor ': '

If neccessary, it can be opened in a viewer/editor which prettyfies it to make
it more human readible.
On the other hand, especially in case it is written manually, it can be saved
prettyfied, the JSON reader will be able to process it.


How to generate lists
=====================

The information bellow is valid only for lists with the key `value-list`.

The lists `value-list` are the biggest part of JSONs. Small `value-list`s or
`value-list`s with random data can be saved directly as lists. However, the most
of the `value-list`s can be generated and the original JSON file can include
only parameters for the generator.

Data in the `value-list`s
-------------------------

The data in the GENERATED lists can be:
- integer constant -> int
- integer constatnt with length 16b -> int16
- IPv4 address -> ip4
- IPv6 address -> ip6
- MAC address -> mac

Two data types are used to define `value-list`s (input information for the
generator):
- list
  - includes values directly used by traffic profile, no other lists are
    generated.

    +--------------+                         +--------------+
    | `value-list` |------------------------>| `value-list` |
    +--------------+                         +--------------+

- dictionary
  - defines parameters used by generator to generate the `value-list`.

    +------------------+    +-----------+    +--------------+
    | dict with params |--->| generator |--->| `value-list` |
    +------------------+    +-----------+    +--------------+

List
....

This possibility is to define any non-deterministic `value-list`. It is not
generated, but taken and used as it is.


Dictionary
..........

The dictinaries include parameters used by generator to generate `value-list`s.

Data types used:

Data type      abbreviation
---------------------------
integer       -> int, int16
IPv4 Address  -> ip4
IPv6 Address  -> ip6
MAC Address   -> mac

Types of lists used:

Type of list                       abbreviation
-----------------------------------------------
the same value repeated N times -> const
sequence of values              -> seq
random values                   -> rnd
intervals of values             -> ivl

Each dictionary includes the key "type" which value is a combination of
`data type` and `type of list` joint by dash '-', e.g.:
- "int-const",
- "ip4-seq",
- "mac-iv1",
- etc.
The `value-list` is generated depending on this `type` and other parameters.


A. The same value repeated `nr` times
.....................................

{
    "type": "<type>-const",
    "value": <int|int16|ip4|ip6|mac>,
    "nr": <int>
}

Generates a list with `value` repeated `nr` times.


B. Sequence
...........

{
    "type": "<type>-seq",
    "start": <int|int16|ip4|ip6|mac>,  # including, if not present, start = 0
    "nr": <int>                  # number of unique items in the generated list
    "repeat": <int>              # if not defined, repeat = 1
}

Generates a list of incremented items starting with `start`, each item is
repeated `repeat` times, e.g.:

{
    "type": "int-seq",
    "start": 10,
    "nr": 10
}
generates:
[10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

and
{
    "type": "int-seq",
    "start": 10,
    "nr": 3,
    "repeat": 2
}
generates:
[10, 10, 11, 11, 12, 12]


C. Random
.........

Not used now. Not implemeted now.

{
    "type": "<type>-rnd",
    "start": <int|int16|ip4|ip6|mac>,  # including, if not present, start = 0
    "end": <int|int16|ip4|ip6|mac>,    # excluding
    "number": <int>                    # number of generated values
    "repeat": <bool>                   # if true, the values can be repeated
                                       # if not defined, repeat = False
}


D. Intervals
............

{
    "type": "<type>-ivl",
    "start": [<int|int16|ip4|ip6|mac>, ],  # list of random values
    "nr": <int>,
    "op": "inc|repeat"
}

Generates a list of groups of items, either repeated (`repeat`) or incremented
(`inc`), e.g.:

{
    "type": "int-ivl",
    "start": [10, 20, 30],
    "nr": 3,
    "op": "inc"
}
generates:
[10, 11, 12, 20, 21, 22, 30, 31, 32]

and
{
    "type": "int-ivl",
    "start": [10, 20, 30],
    "nr": 3,
    "op": "repeat"
}
generates:
[10, 10, 10, 20, 20, 20, 30, 30, 30]

--------------------------------------------------------------------------------

"""


import json

from argparse import ArgumentParser, RawTextHelpFormatter
from ipaddress import IPv4Address, IPv6Address


# Only lists with this key are processed.
THE_KEY = "value-list"


def _format_MAC(mac: int) -> str:
    """Format integer as a MAC address.
    E.g.: 255 -> '00:00:00:00:00:ff'

    :param mac: MAC addres as an integer
    :type mac: int
    :returns: MAC address in format '00:00:00:00:00:ff'
    :rtype: str
    """
    return ":".join([f"{mac:012x}"[i:i + 2] for i in range(0, 12, 2)])


def _func_const(params: dict, dtype: str) -> list:
    """The same value repeated `nr` times

    params = {
        "type": "<type>-const",
        "value": <int|int16|ip4|ip6|mac>,
        "nr": <int>
    }
    Generates a list with `value` repeated `nr` times.

    :param params: A dictionary defining the list.
    :param dtype: Data type.
    :type params: dict
    :type dtype: str
    :returns: Generated list.
    :rtype: list
    """
    _ = dtype
    return [params["value"]] * params["nr"]


def _func_ivl(params: dict, dtype: str) -> list:
    """Intervals

    params = {
        "type": "<type>-ivl",
        "start": [<int|int16|ip4|ip6|mac>, ],  # list of random values
        "nr": <int>,
        "op": "inc|repeat"
    }

    Generates a list of groups of items, either repeated (`repeat`) or
    incremented (`inc`), e.g.:

    {
        "type": "int-ivl",
        "start": [10, 20, 30],
        "nr": 3,
        "op": "inc"
    }
    generates:
    [10, 11, 12, 20, 21, 22, 30, 31, 32]

    and
    {
        "type": "int-ivl",
        "start": [10, 20, 30],
        "nr": 3,
        "op": "repeat"
    }
    generates:
    [10, 10, 10, 20, 20, 20, 30, 30, 30]

    :param params: A dictionary defining the list.
    :param dtype: Data type.
    :type params: dict
    :type dtype: str
    :returns: Generated list.
    :rtype: list
    :raises NotImplementedError: If a function or data type which is not
        implemented is used.
    """

    if params["op"] == "repeat":
        return [itm for itm in params["start"] for _ in range(params["nr"])]
    elif params["op"] == "inc":
        lst = list()
        if dtype == "int":
            for itm in params["start"]:
                for _ in range(params["nr"]):
                    lst.append(itm)
                    itm += 1
            return lst
        elif dtype == "int16":
            for itm in params["start"]:
                for _ in range(params["nr"]):
                    lst.append(itm)
                    itm = 0 if itm == 65535 else itm + 1
            return lst
        elif dtype == "ip4":
            for itm in params["start"]:
                ip_itm = IPv4Address(itm)
                for _ in range(params["nr"]):
                    lst.append(str(ip_itm))
                    ip_itm += 1
            return lst
        elif dtype == "ip6":
            for itm in params["start"]:
                ip_itm = IPv6Address(itm)
                for _ in range(params["nr"]):
                    lst.append(str(ip_itm))
                    ip_itm += 1
            return lst
        elif dtype == "mac":
            for itm in params["start"]:
                int_itm = int(itm.replace(":", ""), 16)
                for _ in range(params["nr"]):
                    lst.append(_format_MAC(int_itm))
                    if int_itm == int("ffffffffffff", 16):
                        int_itm = 0
                    else:
                        int_itm += 1

            return lst
        else:
            raise NotImplementedError(
                f"The data type {dtype} is not defined for function 'ivl'."
            )
    else:
        raise NotImplementedError(
            f"The operation {params['op']} is not defined for function 'ivl'."
        )


def _func_seq(params: dict, dtype: str) -> list:
    """Sequence

    {
        "type": "<type>-seq",
        "start": <int|int16|ip4|ip6|mac>,  # including, if not present, start=0
        "nr": <int>                  # number of unique items in the generated
                                     # list
        "repeat": <int>              # if not defined, repeat = 1
    }

    Generates a list of incremented items starting with `start`, each item is
    repeated `repeat` times, e.g.:

    {
        "type": "int-seq",
        "start": 10,
        "nr": 10
    }
    generates:
    [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

    and
    {
        "type": "int-seq",
        "start": 10,
        "nr": 3,
        "repeat": 2
    }
    generates:
    [10, 10, 11, 11, 12, 12]

    :param params: A dictionary defining the list.
    :param dtype: Data type.
    :type params: dict
    :type dtype: str
    :returns: Generated list.
    :rtype: list
    :raises NotImplementedError: If a data type which is not implemented is
        used.
    """

    start = params.get("start", 0)
    nr = params["nr"]
    repeat = params.get("repeat", 1)
    lst = list()
    if dtype == "int":
        for _ in range(nr):
            lst.append(start)
            start += 1
    elif dtype == "int":
        for _ in range(nr):
            lst.append(start)
            start = 0 if start == 65535 else start + 1
    elif dtype == "ip4":
        ip_start = IPv4Address(start)
        for _ in range(nr):
            lst.append(str(ip_start))
            ip_start += 1
    elif dtype == "ip6":
        ip_start = IPv6Address(start)
        for _ in range(nr):
            lst.append(str(ip_start))
            ip_start += 1
    elif dtype == "mac":
        int_start = int(start.replace(":", ""), 16) if start else 0
        for _ in range(nr):
            lst.append(_format_MAC(int_start))
            if int_start == int("ffffffffffff", 16):
                int_start = 0
            else:
                int_start += 1
    else:
        raise NotImplementedError(
            f"The data type {dtype} is not defined for function 'seq'."
        )

    if repeat == 1:
        return lst
    else:
        return _func_ivl({"start": lst, "nr": repeat, "op": "repeat"}, dtype)


def _func_rnd(params: dict, dtype: str) -> list:
    """Random

    Not used now. Not implemeted now.

    {
        "type": "<type>-rnd",
        "start": <int|int16|ip4|ip6|mac>,  # including, if not present, start=0
        "end": <int|int16|ip4|ip6|mac>,    # excluding
        "number": <int>                    # number of generated values
        "repeat": <bool>                   # if true, the values can be repeated
                                           # if not defined, repeat = False
    }

    :param params: A dictionary defining the list.
    :param dtype: Data type.
    :type params: dict
    :type dtype: str
    :returns: Generated list.
    :rtype: list
    :raises NotImplementedError: Not implemeted now.
    """
    raise NotImplementedError(f"The function 'rnd' is not implemeted.")


def _generate_list(params: dict) -> list:
    """Generates a list of values based on parameters found in the original JSON
    file.

    :param params: A dictionary defining the list.
    :type params: dict
    :raises RuntimeError: If an error occures.
    """

    FUNC = {
        "const": _func_const,
        "ivl": _func_ivl,
        "seq": _func_seq,
        "rnd": _func_rnd
    }

    dtype, func = params["type"].split("-")
    try:
        return FUNC[func](params, dtype)
    except (NotImplementedError, KeyError) as err:
        raise RuntimeError(err)


def process_json(in_data):
    """Traverses through the JSON structure and look for data to process. This
    data has key "THE_KEY" and are defined as dictionaries.

    Data modifications are done inplace.

    :param in_data: JSEON structure to traverse.
    :type in_data: dict
    """

    if isinstance(in_data, dict):
        for key, val in in_data.items():
            if key == THE_KEY and isinstance(val, dict):
                in_data[key] = _generate_list(val)
            else:
                process_json(val)
    elif isinstance(in_data, list):
        for itm in in_data:
            process_json(itm)
    else:
        pass


def _parse_args():
    """Parse the command line arguments.

    :returns: Parsed command line arguments.
    :rtype: Namespace
    """
    parser = ArgumentParser(
        formatter_class=RawTextHelpFormatter,
        description=__doc__
    )
    parser.add_argument(
        "filename", type=str,
        help="The path to JSON file to process."
    )
    return parser.parse_args()


def _main(args):

    with open(args.filename, "rt") as j_file:
        j_data = json.load(j_file)

    process_json(j_data)

    with open(f"new_{args.filename}", "wt") as j_file:
        json.dump(j_data, j_file, separators=(',', ':'))


if __name__ == "__main__":
    _main(_parse_args())
