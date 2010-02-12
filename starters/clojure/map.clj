;; Map =================================================================
;;
;;  translated from the Java version by Nicolas Buduroi

(def width (ref 0))
(def height (ref 0))
(def walls (ref nil))

(defn point [x y] (vector x y))
(defn X [p] (p 0))
(defn Y [p] (p 1))

(defn init-map [w h]
  (dosync
   (ref-set width w)
   (ref-set height h)
   (ref-set walls {})))

(defn wall? [x y]
  (if (or (< x 0) (< y 0)
          (>= x @width) (>= y @height))
    true
    (@walls (point x y))))

(defn set-wall [x y]
  (dosync (alter walls assoc (point x y) true)))

(def players (ref (vec (repeat 2 #(point 0 0)))))

(defn you []  (first  @players))
(defn them [] (second @players))

(defn set-player [n x y]
  (dosync (alter players assoc n (point x y))))

(def directions
     {:north 1
      :east  2
      :south 3
      :west  4})

(defn exit [n] (System/exit n))

(defn error [& message]
  (.println *err* (apply str "FATAL ERROR: " message))
  (.flush *err*)
  (exit 1))

(defn check-game-over [input]
  (when (re-seq #"^(|exit)$" input)
    (exit 1)))

(defn check-first-line [input]
  (when (= 2 (count input))
    (error "The first line of input should be two integers separated "
           "by a space. Instead, got: " input)))

(defn parse-int [s]
  (try (Integer/parseInt s)
       (catch NumberFormatException e
         (error "Can't parse: " s))))

(defn check-line-length [x y]
  (when-not (= x @width)
    (error "Invalid line length: " x " at line " y " should be " @width)))

(defn check-player-found [players-found key]
  (when (players-found key)
    (error "Found two locations for player " key " in the map!")))

(defn check-player-missing [players-found key]
  (when-not (players-found key)
    (error "Did not find a location for player " key "!")))

(defn check-spaces-read [n]
  (when-not (= n (* @width @height))
    (error "Wrong number of spaces in the map.")))

(defn parse-first-line []
  (when-let [line (read-line)]
    (let [first-line (.trim line)
          tokens (seq (.split first-line " "))]
      (check-game-over first-line)
      (check-first-line first-line)
      (apply init-map (map parse-int tokens)))))

(defn initialize []
  (let [read #(.read *in*)]
    (try
     (parse-first-line)
     (loop [x 0 y 0
            players-found {}
            number-of-spaces 0]
       (if (>= y @height)
         (do (check-spaces-read number-of-spaces)
             (check-player-missing players-found \1)
             (check-player-missing players-found \2))
         (let [c (read)]
           (condp = (char c)
             \newline (do (check-line-length x y)
                          (recur 0 (inc y) players-found number-of-spaces))
             \return  (recur x y players-found number-of-spaces)
             \space   (recur (inc x) y players-found (inc number-of-spaces))
             \#       (do (set-wall x y)
                          (recur (inc x) y players-found (inc number-of-spaces)))
             \1       (do (check-player-found players-found \1)
                          (set-player 0 x y)
                          (recur (inc x) y (assoc players-found \1 true) (inc number-of-spaces)))
             \2       (do (check-player-found players-found \2)
                          (set-player 1 x y)
                          (recur (inc x) y (assoc players-found \2 true) (inc number-of-spaces)))
             (if (< c 0)
               (exit 0)
               (error "Invalid character received: " (char c)))))))
     (catch Exception e (error "Unknown exeption: " e)))))

(defn make-move [direction]
  (println (directions direction))
  (flush))
