;; Bot =================================================================
;;
;;  by Nicolas Buduroi

(load "map")

(defn valid-moves [x y]
  [(when-not (wall? x (- y 1)) :north)
   (when-not (wall? (+ x 1) y) :east)
   (when-not (wall? x (+ y 1)) :south)
   (when-not (wall? (- x 1) y) :west)])

(defn compact [coll]
  (filter identity coll))

(defn choose-at-random [coll]
  (let [size (count coll)]
    (when (< 0 size)
      (nth coll (rand-int size)))))

(defn next-move []
  (choose-at-random
   (compact
    (apply valid-moves (you)))))

(defn game-loop []
  (loop []
    (initialize)
    (make-move (next-move))
    (recur)))

(game-loop)
