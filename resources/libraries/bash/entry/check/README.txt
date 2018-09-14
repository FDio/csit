This directory contains checker scripts and other files they need.
Each checker script is assumed to be run from tox,
when working directory is set to ${CSIT_DIR}.
Each script should:
+ Return nonzero exit code when it fails.
++ The tox might ignore the code when the check is not blocking.
+ Write PASSED or FAILED to help with manual execution and debugging.
+ Direct (or tee) verbose output to appropriately named .log file.
+ Write less verbose output to stdout or stderr.
++ TODO: Decide the rules. stderr only perhaps?
++ The level of "less verbose" depends on check and state of codebase.
+ TODO: Should we carefully document which files are
  whitelisted/blacklisted for a particulat check?
