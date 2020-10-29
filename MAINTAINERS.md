MAINTAINERS
===========

This document explains how to do a release:

1. You need a GPG key! If you don't have one, create one.

To do a release X.Y.Z do the following steps:

1. `make start-release VER=vX.Y.Z`
2. edit `ChangeLog` and rename it to TAGMESSAGE`
3. `make complete-release VER=vX.Y.Z.

If for some reason you encounter an error in any of the stages, you can
do:

`make abort-release VER=vX.Y.Z`

