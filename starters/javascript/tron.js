// If you want to use this file, make sure to include it in your
// submission. You may modify it and submit the modified copy, or you
// may discard it and roll your own.

/**
 * Provided code for the JavaScript starter package
 *
 * See the example bots randbot.js and wallbot.js to get started.
 */

var sys = require('sys');

exports.NORTH = 1;
exports.EAST = 2;
exports.SOUTH = 3;
exports.WEST = 4;

exports.FLOOR = ' ';
exports.WALL  = '#';
exports.ME    = '1';
exports.THEM  = '2';

exports.DIRECTIONS = [exports.NORTH, exports.EAST, exports.SOUTH, exports.WEST];

/* Report an error and exit. */

function invalid_input(message) {
    sys.error("Invalid input: " + message);
    process.exit(1);
}

/* Read stdin, and call the supplied callback function
 * for each complete line of input that is read.
 */

function forEachLineOfInput(callback) {
  var buf = "";
  process.stdio.open("ascii");
  process.stdio.addListener("data",
      function (input) {
          var index, line;
          buf = buf + input;
          while ((index = buf.indexOf('\n')) >= 0) {
              line = buf.substring(0, index+1);
              buf = buf.substring(index+1);
              callback(line);
          }
      }
  );
}

/*
 * play the game. Repeatedly read a board from stdin and then
 * call the moveFn callback function with a "board" object.
 */

exports.play = function(moveFn) {
  var lineNumber = 0;
  var width = 0;
  var height = 0;
  var data = "";
  forEachLineOfInput(
      function (line) {
          var dim;
          line = line.replace(/[\r\n]*$/g,''); // Remove end-of-line chars if present
          if (lineNumber === 0) {
              dim = line.split(" ");
              if (dim.length != 2) {
                  invalid_input("expected width, height on first line, got \"" + line + "\"");
              }
              width = parseInt(dim[0],10);
              height = parseInt(dim[1],10);
              if (width <= 0 || isNaN(width) || height <= 0 || isNaN(height)) {
                  invalid_input("expected width, height on first line, got \"" + line + "\"");
              }
          } else {
              if (line.length != width) {
                  invalid_input("malformed board, line wrong length:" + line.length);
              }
              data = data + line;
              if (lineNumber == height) {
                  sys.puts(moveFn(
                  /* The Board object */
                  {
                    /* width of the board */
                    "width": width,
                    /* height of the board */
                    "height": height,
                    /* the raw data of the board as one long string */
                    "data": data,
                    /* Convert a (y, x) coordinate into an index into the data string. */
                    "YXtoCoord": function (y, x) {
                            if (x < 0 || x >= this.width || y < 0 || y >= this.height ) {
                                return -1;
                            }
                            return y * this.width + x;
                        },
                    /* Extract the x value of a coordinate */
                    "coordX": function(coord) {
                            var y = Math.floor(coord / this.width);
                            return coord - y * this.width;
                        },
                    /* Extract the y value of a coordinate */
                    "coordY": function(coord) {
                            return Math.floor(coord / this.width);
                        },
                    /* Look up the given (y, x) coord in the data string. */
                    "atYX": function (y, x) {
                            return this.data.charAt(this.YXToCoord(y, x));
                        },
                    /* Look up the given index in the data string. */
                    "at": function (coord) {
                            if (this.isOutOfBounds(coord)) {
                                return exports.WALL;
                            }
                            return this.data.charAt(coord);
                        },
                    /* Is a given coordinate out of bounds? */
                    "isOutOfBounds": function (coord) {
                            return coord < 0 || coord >= this.data.length;
                        },
                    /* Find the index of a given element. Throws an exception if missing. */
                    "find": function (item) {
                            var index = this.data.indexOf(item);
                            if (index < 0) {
                                throw "Not found";
                            }
                            return index;
                        },
                    /* Return the index of player 1, also known as "me". */
                    "me": function () {
                            return this.find(exports.ME);
                        },
                    /* Return the index of player 2, also known as "them". */
                    "them": function () {
                            return this.find(exports.THEM);
                        },
                    /* Return true if the given index is passable.
                     * out-of-bounds coordinates are not passible.
                     */
                    "passable": function (index) {
                            if (this.isOutOfBounds(index)) {
                                return false;
                            }
                            return this.data[index] == exports.FLOOR;
                        },
                    /* Compute a new index that is in a relative offset from a given origin.
                     * If you don't pass in an origin, it defaults to "me".
                     * If the new index would cross a boundary of the map
                     * the return index is -1.
                     */
                    "rel": function (direction, origin) {
                            if (origin === undefined) {
                                origin = this.me();
                            }
                            if (direction == exports.NORTH) {
                                if (origin < this.width) {
                                    return -1;
                                }
                                return origin - this.width;
                            } else if (direction == exports.SOUTH) {
                                if (origin >= this.data.length - this.width) {
                                    return -1;
                                }
                                return origin + this.width;
                            } else if (direction == exports.EAST) {
                                if (this.coordX(origin) == this.width - 1) {
                                    return -1;
                                }
                                return origin + 1;
                            } else if (direction == exports.WEST) {
                                if (this.coordX(origin) === 0) {
                                    return -1;
                                }
                                return origin - 1;
                            } else {
                                throw "Invalid direction";
                            }
                         },
                     /* Compute all four adjacent locations to a given origin.
                        If the given location is at an edge, some of the adjacent
                        data will become -1.
                      */
                     "adjacent": function (origin) {
                             return [this.rel(exports.NORTH, origin),
                                 this.rel(exports.EAST, origin),
                                 this.rel(exports.SOUTH, origin),
                                 this.rel(exports.WEST, origin)];
                          },
                      /* Return all the possible legal moves from the player's current
                         location. If there are no legal moves, return [tron.NORTH], just
                         to make it easier for simple algorithms.
                       */
                      "moves": function() {
                              var meCoord = this.me();
                              var adjacents = this.adjacent(meCoord);
                              var moves = [];
                              var i;
                              var coord;
                              var dir;
                              for (i = 0; i < adjacents.length; i++) {
                                  dir = exports.DIRECTIONS[i];
                                  coord = adjacents[i];
                                  if (this.passable(coord)) {
                                      moves.push(dir);
                                  }
                              }
                              if (moves.length === 0) {
                                  // it seems we have already lost
                                  return [exports.NORTH];
                              }
                              return moves;
                          }
                  }));
                  // Reset our accumulators.
                  lineNumber = -1;
                  data = "";
              }
          }
          lineNumber += 1;
      });
};
