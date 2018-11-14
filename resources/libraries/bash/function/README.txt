Files in this directory system are to be executed indirectly,
sourced from other scripts.

In fact, the files should only define functions,
except perhaps some minimal logic needed to import dependencies.
The originating function calls should be executed from elsewhere,
typically from entry scripts.
