..
   Copyright (c) 2021 Cisco and/or its affiliates.
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

General rules
^^^^^^^^^^^^^

This document describes a process for CSIT handling of VPP test failures
and regressions. The term "error" is used when distinction between
failure and regression is not important.

Quick fix
~~~~~~~~~

If a person notices an error, but also a quick fix for it,
the person should just contribute a fix, without opening a Jira issue.

Jira ticket
~~~~~~~~~~~

If a quick fix is not feasible, eventually a Jira ticket needs to be opened,
so the information is preserved for future revisitations.

Examples:

Long to merge
-------------

If a quick fix is not merged promptly, due to discussions, complexity
or just a lack of review, Jira ticket should be opened and added to commit message.

No obvious fix
--------------

If a reporter lacks time or expertise to create an appropriate fix,
either other person should pick that work quickly, or a Jira ticket has to be opened.

Consumer demand
---------------

If third parties are asking about an error, a Jira ticket should be opened
to store the answers.

Inactivity
----------

If no progress is made towards fixing the error in some time period,
Jira ticket should be opened, so community is informed (and invited to help).

One-off
-------

In general, errors that happen in only one run have low priority.
After a subsequent no-error runs, CSIT may assume
whatever issue got fixed without opening a Jira ticked.

Roles
^^^^^

The process assumes there are people for the following roles.

Symptom watcher
~~~~~~~~~~~~~~~

A CSIT contributor who periodically reviews daily and weekly job results.
This person does not need to understand the causes of the error.
This person just has to describe what are the visible symptoms,
and which tests are affected.

Symptom watcher is opening "symptom" Jira tickets,
assigning them to CSIT investigator.

When CSIT investigator marks the symptom Jira task as fixed,
symptom watcher verifies daily and weekly runs no longer show the symptom,
and closes the symptom Jira task.

CSIT investigator
~~~~~~~~~~~~~~~~~

A CSIT committer (or contributor) tasked with deeper investigation
of the error. If the error is caused by bad CSIT code, CSIT investigator
should be able to fix it (or delegate to another CSIT committer/contributor).

If CSIT investigator thinks the error is caused by a bad VPP code,
"bug" Jira task is opened and assigned to a VPP developer according to
VPP maintainers file.

When VPP developer marks bug Jira task as done, CSIT investigator
verifies the VPP fix really avoids the error.
Possibly, another error is uncovered by such fix,
requiring new round of investigation and fixing.

VPP developer
~~~~~~~~~~~~~

A VPP contributor tasked with fixing VPP bugs.
The VPP fix may require CSIT changes.

Process
^^^^^^^

Symptom watcher periodically (e.g. one a week) monitors results of daily/weekly jobs
(possibly based on alerting e-mails) and when needed opens (or updates)
symptom Jira tasks.

Symptom watcher, CSIT investigator or other CSIT person
should periodically review activity on both symptom and bug Jira tickets.
For inactive tickets, the assignee should be contacted via various channels
update the status of the Jira task.
