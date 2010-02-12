#lang scheme

(require scheme/port)
(require srfi/13)


; PLAYING
; read board from stdin
; next possible board positions
; evaluate board
; choose move
; write move to stdout
; repeat

; TRAINING


; parsing board
; in cpp, read the first line and parse into width and height
; then read height lines for the board.
; says EOF means the game is over.
;
; the python version reads chunks of chars at a time until it detects a newline, using os.read()
; it strips the chunk (does this strip an EOF or some other weird char?)
; from the chunk it gets a line and parses that into height, width.
; then it reads more chunks until it gets height lines
;
; in python it reads one line at a time until it reaches a line with just an EOF
; a line with something on it before the EOF is an error.
; first line is expected to be 2 ints separated by a space
; reads only h other lines, where h is height from first line.
; if encounters EOF before reading h lines, raises exception
; also checks that the widths equal w, the dimension from the first line.


; spot is an x,y location on the board
; it can contain a wall, a player, or be blank
(define-struct spot (x y) #:transparent)


(define all-spot-types '(wall blank me them))


(define all-moves '(north east south west))


; a board is a matrix of spots.
; it also caches the width, height and spot positions of both players.
; spot 0, 0 is the top left corner of the board.  think pixel coordinates.
(define-struct board
  (width height me them matrix) #:transparent)


; translates a move into the output the game expects
(define (move->string move)
  (case move
    [(north) 1]
    [(east) 2]
    [(south) 3]
    [(west) 4]
    [else (raise 'unknown-move)]))


; translates a spot-type from the input the game provides.
(define (char->spot-type char)
  (case char
    [(#\#) 'wall]
    [(#\space) 'blank]
    [(#\1) 'me]
    [(#\2) 'them]
    [else (raise 'unknown-spot-char)]))


; calculates the position a move would go to.
(define (next-spot curr-spot move)
  (case move
    [(north) (make-spot (spot-x curr-spot) (sub1 (spot-y curr-spot)))]
    [(east) (make-spot (add1 (spot-x curr-spot)) (spot-y curr-spot))]
    [(south) (make-spot (spot-x curr-spot) (add1 (spot-y curr-spot)))]
    [(west) (make-spot (sub1 (spot-x curr-spot)) (spot-y curr-spot))]
    [else (raise 'unknown-move)]))


; not very concise way of saying return matrix[x][y]
(define (board-spot-type curr-spot board)
  (list-ref (list-ref (board-matrix board) (spot-y curr-spot)) (spot-x curr-spot)))


(define (spot-type? curr-spot board type)
  (equal? (board-spot-type curr-spot board) type))


(define (valid-spot? curr-spot board)
  (and (< -1 (spot-x curr-spot) (board-width board))
       (< -1 (spot-y curr-spot) (board-height board))))


(define (can-move? move from-spot board)
  (let ([to-spot (next-spot from-spot move)])
    (and (valid-spot? to-spot board)
	 (spot-type? to-spot board 'blank))))


(define (line->dims line)
  (map string->number (string-tokenize line)))


; get position of me and them.  returns first matching position.
(define (find-matrix-spot matrix spot-type)
  (let row-loop ([y 0] [rows matrix])
    (cond [(empty? rows) (raise "did not find matrix spot type")]
	  [else (let col-loop ([x 0] [cols (first rows)])
		  (cond [(empty? cols) (row-loop (add1 y) (rest rows))]
			[(equal? spot-type (first cols)) (make-spot x y)]
			[else (col-loop (add1 x) (rest cols))]))])))


; translate a board row input into the internal representation
(define (parse-board-line matrix line)
  (append matrix (list (map char->spot-type (string->list line)))))


; translate the input into the internal representation
(define (read-board)
  (let* ([dims (line->dims (read-line))]
	 [width (first dims)]
	 [height (second dims)])
    (let acc-board ([count 0]
		    [matrix '()])
      (cond [(>= count height) (make-board width height (find-matrix-spot matrix 'me) (find-matrix-spot matrix 'them) matrix)]
	    [else (acc-board (add1 count) (parse-board-line matrix (read-line)))]))))


; output a move
(define (write-move move)
  (display (move->string move))
  (newline)
  (display (move->string move) (current-error-port))
  (newline (current-error-port))
  (flush-output))


; main function for cycling through the game.
(define (play strategy)
  (let ([board (read-board)])
    (cond [(empty? board) #f]
	  [else (write-move (strategy board))
		(play strategy)])))


(define (random-strategy board)
  (let ([choices (filter (lambda (move) (can-move? move (board-me board) board)) all-moves)])
    (cond
     [(> (length choices) 0) (list-ref choices (random (length choices)))]
     [else 'north])))


; not a bad strategy ;-)
(define (north-strategy board)
  'north)

; test your bot using mzscheme
; java -jar engine/Tron.jar maps/empty-room.txt "java -jar example_bots/RandomBot.jar" "mzscheme MyTronBot.ss"
(play random-strategy)
