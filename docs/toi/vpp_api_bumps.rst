VPP API Bumps
^^^^^^^^^^^^^

https://wiki.fd.io/view/VPP/ApiChangeProcess
allows CSIT to keep the same API messages over a longer time period.
For release RCA purposes, the period can end on release,
so it can last around one release cycle.

When to bump
------------

After release testing and after RCA for that release is done.

Which new APIs to use
---------------------

When doing bisection, if the start and end are not ordered linearly,
"git bisect" finds last common ancestor. Example for 2101:

  $ cd csit
  $ git bisect start
  $ git checkout master
  $ git bisect new
  $ git checkout rls2101
  $ git bisect old
  Bisecting: a merge base must be tested
  [d910b96c6e5215f0d8961c121f086cd3c2703e43] API: deprecated nsim APIs

In this commit, looking at VPP_STABLE_VER_UBUNTU_BIONIC file
shows the supported VPP version was 21.01-rc0~540-ga8ebb5184.

  $ cd ../vpp
  $ git checkout a8ebb5184

So now have locally checked out the VPP source with messages we can use.
What remains is to manually go through CSIT used messages
to see if there is a newer one.

Example for (old message used in CSIT) ipsec_sad_entry_add_del:

  $ cd ../vpp
  $ fgrep -rn ipsec_sad_entry_add_del | fgrep .api
  src/vnet/ipsec/ipsec.api:192:define ipsec_sad_entry_add_del
  src/vnet/ipsec/ipsec.api:199:define ipsec_sad_entry_add_del_v2
  src/vnet/ipsec/ipsec.api:206:define ipsec_sad_entry_add_del_reply
  src/vnet/ipsec/ipsec.api:212:define ipsec_sad_entry_add_del_v2_reply

Manually look around src/vnet/ipsec/ipsec.api:199 to confirm
there is no newer equivalent message (perhaps with different naming scheme).
There so none (other than the _v2).
Compare arguments of the old and new message,
usually there are only additions with obvious default value.
Update CSIT to use the new message with default values for noew arguments.
If it makes sense for CSIT to provide better values,
add a TODO to do that in a separate change.
