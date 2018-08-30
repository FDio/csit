..
   Copyright (c) 2018 Cisco and/or its affiliates.
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at:
..
       http://www.apache.org/licenses/LICENSE-2.0
..
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

Preable
^^^^^^^

(Currently mostly copy&paste from an e-mail thread.)

CSIT contains many scripts, some in Bash (others in Python)
and some of them are quite complicated.
Complicated Python programs are relative easy to handle
by following pylint recommendations,
basically breaking a monolith code
into functions, classes, modules and packages.

In Bash, it is not that easy.
There are functions, but they are not suited for returning composite objects.
Usually, Bash scripts tend to store all the state
in (local) environment variables.

When I look at a long bash script,
I often see comments breaking the monolith
into blocks and giving them abstracted descriptions.

So in my draft, instead of using comments,
I am sourcing smaller bash script fragments
which contain the abstracted block of code.
The upside is that the fragments can also source other fragments.
The downside is that the developer needs to keep track
of which fragment reads and sets which variables.
Which is also another upside,
because list of variables to interact
is the minimal documentation each fragment should contain.

There are other questions, such as what naming scheme
(for variables and filenames) should the fragments follow,
and how to group fragments into directories.

Proposed style
^^^^^^^^^^^^^^

Bash files should not be monolithic. Generally, there are two types:

+ Entry script: Assumed to be called by user.

  + Sources bash libraries and calls functions defined there.

+ Library file: To be sourced by entry scipts, possibly also by other libraries.

  + Sources other libraries for functions it needs.

    + Or relies on a related file already having sourced that.

    + Documentation should imply which case it is.

  + Defines multiple functions other scripts can call.

Safety
~~~~~~

+ Always quote variable expansions to prevent word splitting.

  + This includes special "variables" such as "${1}".

    + Recommended even if the value is safe, as in "$?" and "$#".

  + It is nice to quote strings in general, so editors can syntax-highlight them.

    + Even if the string is numeric value.

    + Commands and known options can het their own highlight, no need to quote.

      + Example: You do not need to quote every word of
        "pip install --upgrade virtualenv".

  + Do not quote glob characters you need to expand.

    Example: cp "logs"/*".log" "."/

  + Command substitution on right hand side of assignment should be safe
    without quotes.

    + But still, quotes are preferred, unless line length is a concern.

    + Note that command substitution limits the scope for quotes,
      so you do not need to escape them in deeper levels.

  + Avoid situations where word splitting is what you want.

    + Example: Variable holding string of multiple command lines arguments.

    + Use array variable in this case.

    + Expansion uses quotes then: "${name[@]}".

    + Word splitting is allowed when creating arrays from command substitution.

+ Always check the exit code of commands.

  + Traditionally, error code checking is done either by "set -e"
    or by prepending "|| die" after each command.
    The first is unreliable, due to many rules affecting "set -e" behavior
    ( see https://mywiki.wooledge.org/BashFAQ/105 ), but "|| die"
    relies on identifying each command, which is also unreliable.
    When was the last time you checked error code of "echo" command,
    for example?

  + As there is no reliable method of error detection, and there are two
    largely independent unreliable methods, the best what we can do
    is to apply both. So, you should explicitly
    check each command (with "|| die" and similar) AND have "set -e" applied.

  + See below for specific "set -e" recommendations.

+ Use "readlink -e" (or "-f" if target does not exist yet) to normalize
  any path value to absolute path without symlinks. Helps with debugging,
  and identifies malformed paths.

+ Use such normalized paths for sourcing.

+ When exiting on a known error, print a longer, helpful message,
  in order for the user to fix their situation if possible.

+ When error happens at an unexpected place, it is ok for the message
  to be short and generic, instead of speculative.

Bash options
~~~~~~~~~~~~

+ Apply "-x" to make debugging easier.

+ Apply "-e" for early error detection.

  + But still use "|| die" for most commands,
    as "-e" has numerous rules and exceptions.

  + Apply "+e" temporarily for commands which (possibly nonzero)
    exit code we are interested in.

    + Do not forget to store "$?" before calling "set -e" afterwards.

  + "|| true" for benign commands, when we are not interested in exit code.

+ Apply "-u" as unset variable is generally a typo, thus an error.

  + Note that virtualenv activation needs temporary "+u".

+ Apply "-o pipefail" to make sure "-e" picks errors inside piped construct.

+ All together: "set -exuo pipefail".

  + Put that near start of every file, so we are sure
    the options are applied no matter what.

  + Also put it in function bodies and subshell invocations.

Functions
~~~~~~~~~

There are (at least) two possibilities how a code from an external file
can be executed. Either the file contains a code block to execute
on each "source" invocation, or the file just defines a function
which has to be called separately.

The "function way" is considered better, here are some pros and cons:

+ Cons:

  + The function way takes more space. files have more lines,
    and the main code is one indent deeper.

  + It is not easy to create functions for low-level argument manipulation,
    as "shift" command in the function code does not affect caller context.

  + Call sites frequently refer to code two times,
    when sourcing the definition and when executing the function.

  + It is not clear when a library can rely on its relative
    to have performed the sourcing already.

  + Ideally, each library should detect if it has been sourced already
    and return early, which takes even more space.

+ Pros:

  + Some code blocks are more useful when used as function,
    to make call site shorter.

    + Examples: Trap functions, "die" function.

  + The "import" part and "function" part usually have different side effects,
    making the documentation more focused (even if longer overall).

  + There is zero risk of argument-less invocation picking arguments
    from parent context.

    + This safety feature is the main reason for chosing the "function way".

    + This allows code blocks to support optional arguments.

Variables
~~~~~~~~~

Two kinds, local and global.

TODO: Find better adjectives for the two kinds,
if the usual bash meaning is makes reader forget other specifics.

TODO: Should we require typesetting commands, such as "declare" and "local"?

+ Local variables:

  + Lower case names (with underscores).

  + Can be explicitly typeset by "local" builtin command.

    + TODO: Do we want to require this? Name case should suffice.

  + Always initialize before use.

  + Documentation is not required.

  + TODO: Do we need to unset local variables? I think we do not.

+ Global variables:

  + Do not need to be exported (unless external commands need them,
    e.g. PYTHONPATH).

  + Upper case names (with underscores).

  + TODO: Do we need a strict naming convention?

  + Document if a function (or its ineer call) reads a global variable.

  + Document if a function (or its inner call) sets or rewrites a global variable.

  + Set (or rewritten) global variables act as return values of the function.

  + Read global variables act as arguments of the function (but see below).

+ Use curlies (e.g. "${my_variable}").

  + It makes related constructs (such as ${name:-default}) less surprising.

  + It looks more similar to Robot Framework variables (which is good).

Arguments
~~~~~~~~~

Bash scripts and functions accept arguments, named "${1}", "${2}" and so on.
As a whole available as "$@", you can use "shift" command to consume an argument.

Contexts
--------

Functions never have access to parent arguments, but they can read and write
variables set or read by parent contexts.

Arguments or variables
----------------------

+ Both arguments and global variables can act as an input.

+ In general, if the caller is likely to supply the value already placed
  in a global variable of known name, use global variable.

+ Construct "${NAME:-value}" can be used equally well for arguments,
  so default values are possible for both input methods.

+ Arguments are positional, so there are restrictions on which input
  is optional.

+ Functions should either look at arguments (possibly also
  reading global variables to use as defaults), or look at variables only.

+ Do not rely on "${0}", use "${BASH_SOURCE[0]}" instead (and apply "readlink -e")
  to get the current block location.

+ For entry scripts, it is recommended to use standard parsing capabilities.

  + For most Linux distros, "getopt" is fine.

Function size
~~~~~~~~~~~~~

+ In general, use reasoning similar to how pylint limits code complexity.

+ It is recommended to have functions somewhat simpler than Python functions,
  as Bash is generally more verbose and less readable.

+ If you find yourself adding comments in order to partition a block
  into sub-blocks, you should move the sub-blocks to separate functions.

  + Unless your sub-blocks are essentially one-liners,
    not readable just because external commands do not have
    obvious enough parameters.

  + TODO: Do we recommend moving also one-liners into functions?
    Files will be longer, but readability might be worth it.

Documentation
~~~~~~~~~~~~~

+ The library path and filename is visible from source sites, it should be
  descriptive enough.

  + If you have several functions you want to have similar names,
    consider creating a (well-named) sub-library for them.

  + Create deep trees if needed, store common path prefixes into global variable
    to make calling easier.

  + Look at other files in the subdirectory, improve their filenames
    when adding-removing other filenames.

  + Library files should NOT have executable flag set.

  + Library files should have extension .sh (or perhaps .bash).

+ Each entry script should start with a shebang.

  + "#!/bin/usr/env bash" is recommended.

  + Library files should NOT contain a shebang, as they do not execute
    their blocks (without the caller explicitly calling their functions).

+ Following that, there should be a block of comment lines with copyright.

  + Empty line after shebang.

  + It is a boilerplate, but human eyes are good at ignoring it.

  + Overhead for git is also negligible.

+ Following that, "set -exuo pipefail"

  + It acts as an anchor for humans to start paying attention.

Then it depends on script type.

Library documentation
---------------------

+ Following "set -exuo pipefail" comes the "import part" documentation.

+ Then the import code ("source" commands and a bare minimum they need).

+ Then the function definitions, and inside:

  + "set -exuo pipefail" again.

  + Following that the function documentation explaining API contract.
    Similar to Robot [Documentation] or Python function-level docstring.

    + See below.

  + Following that varius TODOs, FIXMEs and code itself.

    + "Code itself" includes comment lines explaining any non-obvious logic.

  + Two empty lines before next function definition.

More details on function documentation:

Generally, explain anything not obvious from the funtion name.

+ Start with short description of function operation or motivation,
  but only if not obvious from function name.

+ Continue with any non-obvious side effect:

  + List global variables read

    + Including descriptions of semantics of their values,
      perhaps mentioning which function is supposed to set them.

    + The "including descriptions" part applies to other items as well.

  + List global variables set, unset, reset, or otherwise updated.

  + Hardcoded values used in code.

    + Not critical, but can hint at future improvements.

  + Files or directories read (so caller can make sure their content is ready).

  + Files or directories updated (created, deleted, wiped, otherwise edited).

  + Functions called (so reader can look them up).

    + Mention where are the functions defined, if not in the current file.

  + External commands executed.

    + Because their behavior can change "out of bounds", meaning
      the contributor changing the implementation of the extrenal command
      can be unaware of this particular function interested in its side effects.

  + Exit code of the last executed command.

    + Usually, most functions should be "pass or die",
      but some callers might be interested in nonzero exit codes
      without using global variables to store them.

    + Remember, "exit 1" ends not only the function, but all scripts
      in the source chain.

      + Prefer calling "die" function. This way the caller can redefine
        that function if there is a good reason for not exiting
        on function failure.

  + TODO: Programs installed, services started, URLs downloaded from, ...

  + TODO: Add more items when you spot them.

  + TODO: Is the current order recommended?

Entry script documentation
--------------------------

+ After "set -exuo pipefail", high-level description.

  + Then TODOs and FIXMEs.

  + Entry scripts are rarely reused, so side effects
    are not that important to document.

+ Then few commented lines to import the library with "die" function.

+ Then block of "source" commands for sourcing other libraries needed.

  + In alphabetical order, place any "special" library
    in the previous block (for "die").

+ Then block of function calls (with parameters).

Other general recommendations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+ Do not repeat yourself, even in documentation:

  + For hardcoded values, write general description (instead of copying the value),
    so when someone edits the value in the code, your description still applies.

  + If affected directory name is taken from a global variable,
    you can distribute the directory description over the two items.

  + If most of side effects come from inner call,
    point the reader to the documentation of the called function.

    + TODO: Composite functions can have large effects. Should we require
      intermediate functions to actively hide them whenever possible?

+ But do repeat yourself if the information crosses functions.

  + Do not skip an item just because the reader should have read
    parent/child documentation already.

  + Frequently it is convenient to copy&paste an item description
    between functions.

  + But sometimes it is useful when descriptions vary. For example:

    + A global variable setter can document how does it figure out the value
      (without caring about what it will be used for by other functions).

    + A global variable reader can document how does it use the value
      (without caring about how has it been figured out by the setter).

+ When possible, make the code look like Python (or Robot Framework).
  Those are three primary languages CSIT code relies on,
  so it is nicer for the readers to see similar expressions when possible.
  Examples:

  + Use indentation, 1 level is 4 spaces.

  + Use "if" instead of "&&" constructs.

  + For comparisons use operators such as "!=" (needs "[[").

+ No more than 80 characters per line.

  + If long commands are needed, use array variables to shorten them.

  + If long strings (or arrays) are needed, use "+=" operator
    to grow the value over few lines.

  + If "|| die" does not fit with all the arguments, use curly braces:

    + Current line has "|| {",

    + Next line has the dire commands (indented one level deeper),

    + Final line closes with "}" at original intent level.

  + TODO: Recommend what to do with other constructs.

    + For example multiple piped commands.

    + No, "eval" is too unsafe to use.
