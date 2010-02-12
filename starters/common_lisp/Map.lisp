;;;; Map.lisp
;;;;
;;;;  author: Erik Winkels (aerique@xs4all.nl)
;;;; created: 2010-02-05
;;;; license: Public Domain
;;;;
;;;; You don't need to edit this file, see the MAKE-MOVE function in
;;;; MyTronBot.lisp.

;;; Package

(defpackage :my-tron-bot
  (:use :cl))

(in-package :my-tron-bot)


;;; Parameters

(defparameter *verbose* nil)

(defparameter *input* *standard-input*)
(defparameter *output* *standard-output*)


;;; Classes

(defclass tron-map ()
  ((map :reader map-of :initarg :map :initform nil)
   (position-1 :reader my-position :initform nil)
   (position-2 :reader enemy-position :initform nil)
   (x :reader x-of :initarg :x :initform nil)
   (y :reader y-of :initarg :y :initform nil)))


(defgeneric make-move (map))
(defgeneric parse-map (map))
(defgeneric print-map (map))
(defgeneric set-map-size (map string))
(defgeneric wall? (map x y))


;;; Utility Functions

(defun current-date-time-string ()
  (multiple-value-bind (sec min hou day mon yea)
      (decode-universal-time (get-universal-time))
    (format nil "~D-~2,'0D-~2,'0D ~2,'0D:~2,'0D:~2,'0D"
            yea mon day hou min sec)))


(let ((log nil))
  (defun logmsg (&rest args)
    (when (and *verbose*
               (not log))
      (setf log (open "sbcl.log" :direction :output :if-exists :append
                                 :if-does-not-exist :create)))
    (when *verbose*
      (format log (with-output-to-string (s) (dolist (a args) (princ a s))))
      (force-output log))))


(defun move (direction)
  (case direction
    (:north (princ "1" *output*))
    (:east  (princ "2" *output*))
    (:south (princ "3" *output*))
    (:west  (princ "4" *output*))
    (:up    (princ "1" *output*))
    (:right (princ "2" *output*))
    (:down  (princ "3" *output*))
    (:left  (princ "4" *output*)))
  (terpri *output*)
  (force-output *output*))


;;; Methods

;; Slow!
(defmethod print-map ((m tron-map))
  (loop repeat (y-of m)
        for y from 0
        do (logmsg "[map] ")
           (loop repeat (x-of m)
                 for x from 0
                 do (logmsg (aref (map-of m) x y)))
           (logmsg "~%")))


(defmethod set-map-size ((m tron-map) (s string))
  (let ((space (position #\space s)))
    (setf (slot-value m 'x) (parse-integer (subseq s 0 space))
          (slot-value m 'y) (parse-integer (subseq s space)))))


(defmethod parse-map ((m tron-map))
  (if (and (x-of m) (y-of m))  ;; do we know the map's size?
      (read-line *input* nil nil)
      (set-map-size m (read-line *input* nil nil)))
  (unless (map-of m)  ;; is the map array initialised?
    (setf (slot-value m 'map)
          (make-array (list (x-of m) (y-of m)))))
  (loop repeat (y-of m)
        for y from 0
        do (loop for c across (read-line *input* nil nil)
                 for x from 0
                 do (setf (aref (map-of m) x y) c)
                    (case c
                      (#\1 (setf (slot-value m 'position-1) (list x y)))
                      (#\2 (setf (slot-value m 'position-2) (list x y)))))))


(defmethod wall? ((m tron-map) (x fixnum) (y fixnum))
  (or (equal (aref (map-of m) x y) #\#)
      ;; we count the player's as a wall as well
      (equal (aref (map-of m) x y) #\1)
      (equal (aref (map-of m) x y) #\2)))
