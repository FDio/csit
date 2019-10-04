# FD.io CSIT migration Python 2.7 to Python 3

## Python3 version

There is a pre-agreement to migrate to Python 3.5 ([v3.5.7](https://docs.python.org/3.5/whatsnew/changelog.html#python-3-5-7-final) 
is the last final release at the moment). However Python 3.6 ([v3.6.9](https://docs.python.org/3.6/whatsnew/changelog.html#python-3-6-9-final) 
is the last final release at the moment) contains some improvements that could be interesting for CSIT:

- formatted strings (f-strings):
  ```
  f"He said his name is {name}."
  # instead of
  "He said his name is {n}.".format(n=name)
  ```
- the `dict` type has been re-implemented to use a more compact representation
  resulted in dictionaries using 20% to 25% less memory compared to Python 3.5
- type annotations of function parameters and variables (type hints):
  ```python
  primes: List[int] = []
  captain: str  # Note: no initial value!
  class Starship:
      stats: Dict[str, int] = {}
  def greeting(name: str) => str:  # Return type defined too
      return 'Hello ' + name
  ```

## Dependency libs

There was used *[caniusepython3](https://pypi.org/project/pypcap/)* tool to 
check readiness of current version of csit external libraries for Python 3. It 
identified one external library that needs to be updated to support Python 3:
  ```
 (env) vpp@vpp-VirtualBox:~/Documents/csit$ caniusepython3 -r requirements.txt
 Finding and checking dependencies ...
 You need 1 project to transition to Python 3.
 Of that 1 project, 1 has no direct dependencies blocking its transition:
   pypcap
 (env) vpp@vpp-VirtualBox:~/Documents/csit$
 ```
 
 The latest released version of *[pypcap](https://pypi.org/project/pypcap/)* is 
 version 1.2.3 (Python 3 support implemented in version 1.2.0).
 
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

1. Update pypcap library - week before the week W
1. Install agreed Python 3 version to all servers used by CSIT for test 
   execution - week before the week W
   1. vpp device servers
   1. performance testbeds
   1. virl server(s) - if still in use
   1. jenkins executors - needed co-operation with Ed Kern
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
