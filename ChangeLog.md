
# Change log

## Version 3.2.1

Minor release:

* Use mdToRst for package description generation

## Version 3.2.0

First production release:

* Introduce command/service architecture
* Implement demo examples with proxy servers
* Improve readme files

## Version 3.1.0

Beta version release:

* Continue code refactor and cleanups
* Get all using tests working reliably
* Identify Known Issues and Limitations (KIL)
* Update README to reflect generic audience

## Version 3.0.0

Fork from pyzmqrpc and initial release:

* Refactor code and drop Python 2.x support
* Use github actions for CI
* Split the unit tests and get VSCode dev env working
* Disable all failing unit tests and mark library as alpha release

## Version 2.0.0

* Python 3 compatibility added.
* Added to Travis CI

## Version 1.5.1

* Fixed heartbeat reception in ZmqRpcServer.

## Version 1.5.0

* Improved ability to use heartbeats to avoid silently failing ZMQ sockets.
Timeouts can now be set per SUB socket.
Before this version a reset would be for all addresses in the SUB address
list provided.
This would allow a single socket to get disconnected and never
reconnected because the other SUB sockets were still getting messages.
* Replace * with 0.0.0.0 in socket.unbind, which seems no longer supported.

## Version 1.0.1

* Central logging for entire zmqrpc facility
* Also logs exceptions for easier debugging.

## Version 1.0.0

* Added a buffered REQ/REQ proxy which uses PUB/SUB internally.
* Bumped version number to stable release number since the library worked
fine for months and code and tests are now at a more mature level.

## Version 0.1.9 and before

* Internal testing.
