# The Makefile
#
# If you're using Windows and you don't know what this file is,
# don't worry about it. Just use Visual C++ Express Edition or
# Dev-C++ to work on your code.

MyTronBot:
	sbcl --dynamic-space-size 2000 --no-userinit --no-sysinit --noprint --disable-debugger --load MyTronBot.lisp --eval "(save-lisp-and-die \"MyTronBot\" :executable t :toplevel #'my-tron-bot::main)"
