# FD.io CSIT migration Python 2.7 to Python 3

## Python 3 version

There is a pre-agreement to migrate to Python 3 version used by
Ubuntu 18.04-LTS - currently it is version [3.6.8](https://docs.python.org/3.6/whatsnew/changelog.html#python-3-6-8-final).

CentOS7 version 1810 that is used in [FD.io](https://fd.io/) also contains
Python 3.6.

## Dependency libs

There was used *[caniusepython3](https://pypi.org/project/caniusepython3/)*
tool to check readiness of current version of csit external libraries for
Python 3. It identified one external library that needs to be updated to
support Python 3:
  ```
 (env) vpp@vpp-VirtualBox:~/Documents/csit$ caniusepython3 -r requirements.txt
 Finding and checking dependencies ...
 You need 1 project to transition to Python 3.
 Of that 1 project, 1 has no direct dependencies blocking its transition:
   pypcap
 (env) vpp@vpp-VirtualBox:~/Documents/csit$ caniusepython3 -r tox-requirements.txt 
 Finding and checking dependencies ...
 You have 0 projects blocking you from using Python 3!
 (env) vpp@vpp-VirtualBox:~/Documents/csit$
 ```

The latest released version of *[pypcap](https://pypi.org/project/pypcap/)* is
version 1.2.3 (Python 3 support implemented in version 1.2.0).

Packages were checked for Python 3.6.8 support too and here are proposed
package versions:

- directly needed packages
  - ecdsa==0.13.3
  - paramiko==2.6.0
  - pycrypto==2.6.1
  - pypcap==1.2.3    # min. v1.2.0 for Python 3.6 support
  - PyYAML==5.1
  - requests==2.22.0 # min. v2.14.0 for Python 3.6 support
  - robotframework==3.1.2
  - scapy==2.4.3     # min. v2.4.0 for Python 3.6 support
  - scp==0.13.2

- directly needed packages for PLRSearch
  - dill==0.3.1.1
  - numpy==1.17.3    # v1.14.5 - compatibility with Python 3.6.2, possible
    incompatibility with Python 3.6.8; v1.14.6 should be compatible with
    Python 3.6.8
  - scipy==1.3.1

- directly needed packages for PAL
  - hdrhistogram==0.6.1
  - pandas==0.25.3
  - plotly==4.1.1
  - PTable==0.9.2
  - Sphinx==2.2.1
  - sphinx-rtd-theme==0.4.0
  - sphinxcontrib-programoutput==0.15

- packages needed by paramiko package
  - bcrypt==3.1.7
  - cffi==1.13.1
  - cryptography==2.8
  - pycparser==2.19
  - PyNaCl==1.3.0
  - six==1.12.0

- packages needed by request package
  - certifi==2019.9.11
  - chardet==3.0.4
  - idna==2.8
  - urllib3==1.25.6

- not needed anymore
  - aenum - enum module in Python 3.6 already contains needed enum types
  - ipaddress - module already included in Python 3.6
  - pexpect - can be removed when corresponding unused code is removed from
    ssh.py
  - pykwalify + docpot + python-dateutil - can be removed if virl not used
    anymore

After discussion there is an agreement to use pip freeze for indirect
dependencies when all direct dependency versions are resolved - see example of
*[requirements.txt](https://gerrit.fd.io/r/c/csit/+/23207/17/requirements.txt)*
file in CSIT gerrit commit
[Python3: PIP requirement](https://gerrit.fd.io/r/c/csit/+/23207).

## Required CSIT code changes

There were identified following code changes that need to be addressed during
Python 2.7 to Python 3 migration in CSIT:
- imports relative to package
  - `import submodul1` => `from . import submodule1`
  - `from csv import my_csv` => `from .csv import my_csv`
- StringIO
  - `import StringIO` => `from io import StringIO`
- `StandardError` -=> `Exception`
- raising  exceptions - should be ready
  - `raise ValueError, "wrong value"` => `raise ValueError("wrong value")`
- catching exceptions - should be ready
  - `except ValueError, e:` => `except ValueError as e:`
- integers
  - `long` => `int`
- strings and bytes
  - `unicode` => `str`
  - `basestring` => `str`
  - `str` => `bytes` - not generally, only if bytes type really required
  - use following string style conventions:
    - `u"a unicode string literals"`
    - `b"a bytes string literals"`
    - `f"a formatted unicode string literals"` - `f"He said his name is {name}"`
       instead of `"He said his name is {n}".format(n=name)`
- integer division with rounding down
  - `2 / 3` =>  `2 // 3`
- metaclasses - use only new style
  - `class Form(BaseForm, metaclass=FormType):`
- for-loop variables and the global namespace leak
  - for-loop variables don't leak into the global namespace anymore
- returning iterable objects instead of lists
  - `xrange` => `range`
  - `range` => `list(range())`
  - `map` => `list(map())`
  - `zip` => `list(zip())`
  - `filter` => `list(filter())`
  - dictionaries
    - `.iteritems()` => `.items()`
    - `.iterkeys()` => `.keys()`
    - `.itervalues()` => `.values()`
    - `.viewitems()` => `.items()`
    - `.viewkeys()` => `.keys()`
    - `.viewvalues()` => `.values()`
    - `.items()`=> `list(.items())`
    - `.keys()` => `list(.keys())`
    - `.values()` => `list(.values())`
    - `dict.has_key(key)` => `key in dict`
  - lists
    - `L = list(some_iterable); L.sort()` => `L = sorted(some_iterable)`
    - parenthesis in list comprehensions
      - `[... for var in item1, item2, ...]` => `[... for var in (item1, item2, ...)]`
- file IO with `open`
  - `f = open('myfile.txt')  # f.read() returns byte string` =>
  `from io import open` plus
    - `f = open('myfile.txt', 'rb')  # f.read() should return bytes`
    - `f = open('myfile.txt', 'rt')  # f.read() should return unicode text`
- reduce()
  - `reduce()` => `from functools import reduce; reduce()`

- python files in following directories:
  - resources/libraries/python
  - resources/tools
  - resources/traffic_profiles/trex
  - resources/traffic_scripts

- check python calls in bash files:
  - resources/libraries/bash/
  - csit root directory

## Migration steps

1. Update all external libraries - week(s) before the week W
1. Install agreed Python 3 version to all servers used by CSIT for test
   execution - week(s) before the week W
   1. vpp device servers - already done
   1. performance testbeds - already done
   1. jenkins executors - already done
1. Freeze the CSIT master branch for one week for commits other then Python 2 to
   Python 3 migration - week W
   1. Create back up branch of actual master
   1. Migrate libraries - work split between all available CSIT developers. Each
      one will submit separate commit for review - csit-vpp-xxx verify jobs will
      be failing at this phase so committers will need to overwrite verify
      voting to be able to merged these commits.

      TODO: provide separate spread sheet with listed libraries to be migrated
      with the name of CSIT developer responsible for the migration of this
      library.
   1. Run jobs and tests of all of types when all libraries migrated to confirm
      functionality or to catch bugs that needs to be fixed - iterate until
      successful execution of all tests.
1. Unfreeze the CSIT master branch.
