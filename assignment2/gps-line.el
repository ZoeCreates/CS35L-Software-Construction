(defun gps-line ()
  "Print the current buffer line number and total number of lines."
  (interactive)
  (let ((current-line (line-number-at-pos))
        (total-lines (count-lines (point-min) (point-max))))
    (message "Line %d/%d" current-line total-lines)))
