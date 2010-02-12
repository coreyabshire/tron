#!/bin/sh

if [ -x MyTronBot ]; then
    java -jar engine/Tron.jar maps/u.txt "./MyTronBot" "java -jar example_bots/RunAway.jar";
else
    java -jar engine/Tron.jar maps/u.txt "sbcl --noinform --noprint --no-userinit --no-sysinit --disable-debugger --load MyTronBot.lisp --eval \"(my-tron-bot::main)\"" "java -jar example_bots/RunAway.jar";
fi
