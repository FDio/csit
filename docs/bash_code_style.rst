..
   Copyright (c) 2019 Cisco and/or its affiliates.
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


The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED",
"MAY", and "OPTIONAL" in this document are to be interpreted as
described in `BCP 14 <https://tools.ietf.org/html/bcp14>`_
`[RFC2119] <https://tools.ietf.org/html/rfc2119>`_
`[RFC8174] <https://tools.ietf.org/html/rfc8174>`_
when, and only when, they appear in all capitals, as shown here.

This document SHALL describe guidelines for writing reliable, maintainable,
reusable and readable code for CSIT.

TODO: Decide whether to use "you SHALL", "contributors SHALL",
or "code SHALL be"; convert other forms to the chosen one.

Motivation
^^^^^^^^^^

TODO: List reasons why we need code style document for Bash.

Proposed style
^^^^^^^^^^^^^^

File types
~~~~~~~~~~

Bash files SHOULD NOT be monolithic. Generally, this document
considers two types of bash files:

+ Entry script: Assumed to be called by user, or a script "external" in some way.

  + Sources bash libraries and calls functions defined there.

+ Library file: To be sourced by entry scipts, possibly also by other libraries.

  + Sources other libraries for functions it needs.

    + Or relies on a related file already having sourced that.

    + Documentation SHALL imply which case it is.

  + Defines multiple functions other scripts can call.

Safety
~~~~~~

+ Variable expansions MUST be quoted, to prevent word splitting.

  + This includes special "variables" such as "${1}".

    + RECOMMENDED even if the value is safe, as in "$?" and "$#".

  + It is RECOMMENDED to quote strings in general,
    so text editors can syntax-highlight them.

    + Even if the string is a numeric value.

    + Commands and known options can get their own highlight, no need to quote.

      + Example: You do not need to quote every word of
        "pip install --upgrade virtualenv".

  + You SHALL NOT quote glob characters you need to expand (obviously).

    + OPTIONALLY do not quote adjacent characters (such as dot or fore-slash),
      so that syntax highlighting makes them stand out compared to surrounding
      ordinary strings.

    + Example: cp "logs"/*."log" "."/

    + TODO: Consider giving examples both for good and bad usage.

  + Command substitution on right hand side of assignment should be safe
    without quotes.

    + But still, quotes are RECOMMENDED, unless line length is a concern.

    + Note that command substitution limits the scope for quotes,
      so you are NOT REQUIRED to escape the quotes in deeper levels.

    + TODO: Do we prefer backtics, or "dollar round-bracket"?

      + Backticks are more readable, especially when there are
        round brackets in the surrounding text.

      + Backticks do not allow nested command substitution.

        + But we might want to avoid nested command substitution anyway?

  + You SHOULD NOT structure your code is a way where
    word splitting is what you want.

    + Example: Variable holding string of multiple command lines arguments.

    + Solution: Use array variable in this case.

    + Expansion MUST use quotes then: "${name[@]}".

    + Word splitting MAY be used when creating arrays from command substitution.

+ You SHALL always check the exit code of commands.

  + Traditionally, error code checking is done either by "set -e"
    or by appending "|| die" after each command.
    The first is unreliable, due to many rules affecting "set -e" behavior
    (see <https://mywiki.wooledge.org/BashFAQ/105>), but "|| die"
    relies on humans identifying each command, which is also unreliable.
    When was the last time you checked error code of "echo" command,
    for example?

  + As there is no reliable method of error detection, and there are two
    largely independent unreliable methods, the best what we can do
    is to apply both. So, you SHOULD explicitly
    check each command (with "|| die" and similar) AND have "set -e" applied.

  + You MUST explicitly check each command, unless the command is well known,
    and considered safe (such as the aforementioned "echo").

  + See below for specific "set -e" recommendations.

+ You SHOULD use "readlink -e" (or "-f" if target does not exist yet)
  to normalize any path value to absolute path without symlinks.
  Helps with debugging, and identifies malformed paths.

+ You SHOULD use such normalized paths for sourcing.

+ When exiting on a known error, you MUST print a longer, helpful message,
  in order for the user to fix their situation if possible.

+ When error happens at an unexpected place, it is RECOMMENDED for the message
  to be short and generic, instead of speculative.

Bash options
~~~~~~~~~~~~

+ You MUST apply "-x" to make debugging easier.

  + You MAY temporarily supress such output in order to avoid spam
    (e.g. in long busy loops), but it is still NOT RECOMMENDED to do so.

+ You MUST apply "-e" for early error detection.

  + But you still SHOULD use "|| die" for most commands,
    as "-e" has numerous rules and exceptions.

  + You MAY apply "+e" temporarily for commands which (possibly nonzero)
    exit code we are interested in.

    + You MUST to store "$?" and call "set -e" immediatelly afterwards.

  + You MAY append "|| true" for benign commands,
    when it is clear we are not interested in exit code.

+ You MUST apply "-u" as unset variable is generally a typo, thus an error.

  + You MAY temporarily apply "+u" if a command needs that to pass.

  + Virtualenv activation is the only known example so far.

+ You MUST apply "-o pipefail" to make sure "-e" picks errors
  inside piped construct.

  + You MAY use "|| true" inside a pipe construct, in the (inprobable) case
    when non-zero exit code still results in a meaningful pipe output.

+ All together: "set -exuo pipefail".

  + You MUST put that line near start of every file, so we are sure
    the options are applied no matter what.

    + "Near start" means "before any nontrivial code".

    + Basically only copyright and long high-level comments are
      RECOMMENDED to appear before.

  + Also you MUST put the line near start of function bodies
    and subshell invocations.

Functions
~~~~~~~~~

There are (at least) two possibilities how a code from an external file
can be executed. Either the file contains a code block to execute
on each "source" invocation, or the file just defines a function
which has to be called separately.

This document considers the "function way" to be better,
here are some pros and cons:

+ Cons:

  + The function way takes more space. Files have more lines,
    and the code in function body is one indent deeper.

  + It is not easy to create functions for low-level argument manipulation,
    as "shift" command in the function code does not affect the caller context.

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

TODO: Translate the "function way" into list of rules.

Variables
~~~~~~~~~

This document describes two kinds of variables: called "local" and "global".

TODO: Find better adjectives for the two kinds defined here,
if the usual bash meaning makes reader forget other specifics.
For example, variable with lowercase name and not marked by "local" builtin,
is cosidered "global" from bash point of view, but "local" from this document
point of view.

+ Local variables:

  + Variable name MUST contain only lower case letters and underscores.

    + TODO: Do we allow digits?

  + You MUST NOT export local variables.

  + You MUST NOT rely on local variables set in different contexts.

  + Documentation is NOT REQUIRED.

    + Variable name SHOULD be descriptive enough.

  + It MUST be initialized before first use.

    + You SHOULD add a comment if a reader might have missed the initialization.

  + TODO: Agree on level of defensiveness (against local values
    being influenced by other functions) needed.
    Possible alternatives / additions to the "always initialize" rule:

    + Unset local variables when leaving the function.

    + Explicitly typeset by "local" builtin command.

    + Require strict naming convention, e.g. function_name__variable_name.

+ Global variables:

  + Variable name MUST contain only upper case letters and underscores.

    + TODO: Do we allow digits?

  + They SHOULD NOT be exported, unless external commands need them
    (e.g. PYTHONPATH).

  + TODO: Propose a strict naming convention, or a central document
    of all used global variables, to prevent contributors
    from causing variable name conflicts.

  + You MUST document if a function (or its inner call) reads a global variable.

  + You MUST document if a function (or its inner call)
    sets or writes a global variable.

  + If a function "wants to return a value", it SHOULD be implemented
    as the function setting (or rewriting) a global variable,
    and the call sites reading that variable.

  + If a function "wants to accept an argument", it IS RECOMMENDED
    to be implemented as the call sites setting or rewriting global variables,
    and the function reading that variables.
    But see below for direct arguments.

+ Use MUST use curly brackets when referencing variables, e.g. "${my_variable}".

  + It makes related constructs (such as ${name:-default}) less surprising.

  + It looks more similar to Robot Framework variables (which is good).

Arguments
~~~~~~~~~

Bash scripts and functions MAY accept arguments, named "${1}", "${2}" and so on.
As a whole available via "$@".
You MAY use "shift" command to consume an argument.

Contexts
````````

Functions never have access to parent arguments, but they can read and write
variables set or read by parent contexts.

Arguments or variables
``````````````````````

+ Both arguments and global variables MAY act as an input.

+ In general, if the caller is likely to supply the value already placed
  in a global variable of known name, it is RECOMMENDED to use a global variable.

+ Construct "${NAME:-value}" can be used equally well for arguments,
  so default values are possible for both input methods.

+ Arguments are positional, so there are restrictions on which input
  is optional.

+ Functions SHOULD either look at arguments (possibly also
  reading global variables to use as defaults), or look at variables only.

+ You MUST NOT rely on "${0}", use "${BASH_SOURCE[0]}" instead
  (and apply "readlink -e") to get the current block location.

+ For entry scripts, it is RECOMMENDED to use standard parsing capabilities.

  + For most Linux distros, "getopt" is RECOMMENDED.

Function size
~~~~~~~~~~~~~

+ In general, you SHOULD use reasoning similar to how pylint
  limits code complexity.

+ It is RECOMMENDED to have functions somewhat simpler than Python functions,
  as Bash is generally more verbose and less readable.

+ If you find yourself adding comments in order to partition a block
  into sub-blocks, you SHOULD move the sub-blocks to separate functions.

  + Unless your sub-blocks are essentially one-liners,
    not readable just because external commands do not have
    obvious enough parameters. Use common sense.

Documentation
~~~~~~~~~~~~~

+ The library path and filename is visible from source sites. It SHOULD be
  descriptive enough, so reader do not need to look inside to determine
  how and why is the sourced file used.

  + If you have several functions you want to have similar names,
    you are RECOMMENDED to create a (well-named) sub-library for them.

  + You MAY create deep trees if needed, you SHOULD store common path prefixes
    into global variables to make sourcing easier.

  + Look at other files in the subdirectory, you SHOULD improve their filenames
    when adding-removing other filenames.

  + Library files SHOULD NOT have executable flag set.

  + Library files SHOULD have an extension .sh (or perhaps .bash).

+ Each entry script MUST start with a shebang.

  + "#!/bin/usr/env bash" is recommended.

  + You SHOULD put an empty line after shebang.

  + Library files SHOULD NOT contain a shebang, as they do not execute
    their blocks (without the caller explicitly calling their functions).

+ Following that, there SHOULD be a block of comment lines with copyright.

  + It is a boilerplate, but human eyes are good at ignoring it.

  + Overhead for git is also negligible.

+ Following that, there MUST be "set -exuo pipefail".

  + It acts as an anchor for humans to start paying attention.

Then it depends on script type.

Library documentation
`````````````````````

+ Following "set -exuo pipefail" SHALL come the "import part" documentation.

+ Then SHALL be the import code ("source" commands and a bare minimum they need).

+ Then SHALL be the function definitions, and inside:

  + "set -exuo pipefail" again.

  + Following that SHALL be the function documentation explaining API contract.
    Similar to Robot [Documentation] or Python function-level docstring.

    + See below.

  + Following that SHALL be varius TODOs, FIXMEs and code itself.

    + "Code itself" SHALL include comment lines explaining any non-obvious logic.

    + TODO: Document (in an appropriate place) how TODOs differ from FIXMEs.

  + There SHALL be two empty lines before next function definition.

More details on function documentation:

Generally, you SHOULD explain anything not obvious from the funtion name.

+ You SHOULD start with short description of function operation or motivation,
  but only if not obvious from function name.

+ You SHOULD continue with any non-obvious side effect:

  + You MUST list all read global variables.

    + You SHOULD include descriptions of semantics of their values.
      It is RECOMMENDED to mention which function is supposed to set them.

    + The "including descriptions" part applies to other items as well.

  + You MUST list all global variables set, unset, reset, or otherwise updated.

  + It is RECOMMENDED to list all hardcoded values used in code.

    + Not critical, but can hint at future improvements.

  + You MUST list all files or directories read
    (so caller can make sure their content is ready).

  + You MUST list all files or directories updated
    (created, deleted, emptied, otherwise edited).

  + You SHOULD list all functions called (so reader can look them up).

    + You SHOULD mention where are the functions defined,
      if not in the current file.

  + You SHOULD list all external commands executed.

    + Because their behavior can change "out of bounds", meaning
      the contributor changing the implementation of the extrenal command
      can be unaware of this particular function interested in its side effects.

  + You SHOULD explain exit code (coming from the last executed command).

    + Usually, most functions SHOULD be "pass or die",
      but some callers MAY be interested in nonzero exit codes
      without using global variables to store them.

    + Remember, "exit 1" ends not only the function, but all scripts
      in the source chain, so you MUST NOT use it for other purposes.

      + You SHOULD call "die" function instead. This way the caller can redefine
        that function, if there is a good reason for not exiting
        on function failure.

  + TODO: Programs installed, services started, URLs downloaded from, ...

  + TODO: Add more items when you spot them.

  + TODO: Is the current order recommended?

Entry script documentation
``````````````````````````

+ After "set -exuo pipefail", high-level description SHALL come.

  + Then TODOs and FIXMEs SHALL be placed (if any).

  + Entry scripts are rarely reused, so detailed side effects
    are OPTIONAL to document.

+ Then SHALL come few commented lines to import the library with "die" function.

+ Then block of "source" commands for sourcing other libraries needed SHALL be.

  + In alphabetical order, any "special" library SHOULD be
    in the previous block (for "die").

+ Then SHALL come block of function calls (with parameters).

Other general recommendations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+ You SHOULD NOT not repeat yourself, even in documentation:

  + For hardcoded values, you SHOULD write a general description
    (instead of copying the value), so when someone edits the value
    in the code, your description still applies.

  + If affected directory name is taken from a global variable,
    you MAY distribute the directory description over the two items.

  + If most of side effects come from an inner call,
    you MAY point the reader to the documentation of the called function
    (instead of listing all the side effects).

    + TODO: Composite functions can have large effects. Should we require
      intermediate functions to actively hide them whenever possible?

+ But you SHOULD repeat yourself if the information crosses functions.

  + Do MUST NOT not skip an item just because the reader should have read
    parent/child documentation already.

  + Frequently it is RECOMMENDED to copy&paste an item descriptions
    between functions.

  + But sometimes it is RECOMMENDED to vary the descriptions. For example:

    + A global variable setter MAY document how does it figure out the value
      (without caring about what it will be used for by other functions).

    + A global variable reader MAY document how does it use the value
      (without caring about how has it been figured out by the setter).

+ When possible, you SHOULD make the code look like Python (or Robot Framework).
  Those are three primary languages CSIT code relies on,
  so it is nicer for the readers to see similar expressions when possible.
  Examples:

  + You MUST use indentation, 1 level is 4 spaces.

  + You SHOULD use "if" instead of "&&" constructs.

  + For comparisons you SHOULD use operators such as "!=" (needs "[[").

+ You MUST NOT use more than 80 characters per line.

  + If long commands are needed, you SHOULD use array variables to shorten them.

  + If long strings (or arrays) are needed, you SHOULD use "+=" operator
    to grow the value over few lines.

  + If "|| die" does not fit with the command, you SHOULD use curly braces:

    + Current line has "|| {",

    + Next line has the die commands (indented one level deeper),

    + Final line closes with "}" at original intent level.

  + TODO: Recommend what to do with other constructs.

    + For example multiple piped commands.

    + No, "eval" is too unsafe to use.
