;;;; MyTronBot.lisp
;;;;
;;;;  author: Erik Winkels (aerique@xs4all.nl)
;;;; created: 2010-02-05
;;;; license: Public Domain
;;;;    note: Tested on SBCL 1.0.31.0.debian and 1.0.29 on Windows Vista.
;;;;
;;;; usage: sbcl --script MyTronBot.lisp

(load "Map.lisp")

(in-package :my-tron-bot)


;;; Debugging Switch
;;;
;;; Set this to 't' if you want debugging output written to "sbcl.log" and
;;; for the LOGMSG function to actually do something.
;;;
;;; LOGMSG always appends lines to the log so you can just keep a "tail -f
;;; sbcl.log" running.

(setf *verbose* nil)  ; Set to NIL when submitting!


;;; Functions & Methods

;; MAKE-MOVE is where you come in.  For now it only prints some debugging info
;; and the map to "sbcl.log" if *verbose* is set to T and always moves the
;; player left.
;;
;; The MOVE function announces your move to the tournament engine so this
;; is generally the last thing you do in this function.  Possible moves are:
;; :north, :east, :south, :west, :up, :right, :down and :left.

(defmethod make-move ((m tron-map))
  (logmsg "   my position: " (my-position m) "~%"
          "enemy position: " (enemy-position m) "~%")
  (print-map m)
  (move :left))


;;; Main Program
;;;
;;; You don't need to edit part.  It takes care of communication with the
;;; tournament engine.

(defun main ()
  (logmsg "~&~%=== New Match: " (current-date-time-string) " ===~%")
  (loop with map = (make-instance 'tron-map)
        while (peek-char nil *input* nil nil)
        for move from 0
        do (logmsg "--- move: " move " ---~%")
           (parse-map map)
           (make-move map)))
