Google AI Challenge in Clojure
------------------------------

This is a sample starter package for the 2010 Google AI Challenge in
Clojure. If I get more time I'll update it with more translated example
bots or some of my own.

To make it work you'll have to add a jar of Clojure 1.1 (not tested with
1.0 but it should work) in a folder called deps. I've only tested it
with the included clj.bat under Cygwin in Windows XP, it should be
pretty easy to make it a bash script to work elsewhere.

You can test the provided bot using:

    java -jar engine/Tron.jar maps/empty-room.txt "./clj.bat MyTronBot.clj" "./clj.bat MyTronBot.clj"
