
# Run the single statements
echo "CHECKING single_stmts"
cat single_stmts.txt | python grove.py > trash.txt

# Run the single expressions
#
# cat singles.txt | python grove.py 
# sends the text in singles.txt to your interpreter,
#   as if the user was typing it
#
# | %{$_ -replace "Grove>> ",""}
# takes the output from your interpreter and replaces the prompt
#   with the empty string
#
# > singles_mine.txt
# saves that output to the file singles_mine.txt
echo "CHECKING singles"
cat singles.txt | python grove.py | %{$_ -replace "Grove>> ",""}  > singles_mine.txt

# Compare the single expressions' results
# You can also use a program like kdiff3 to show differences
diff (cat singles_answers.txt) (cat singles_mine.txt)


# Now repeat the comparison for each of the test cases
foreach ($num in 1,2,3,4,5,6) {
  echo "CHECKING test${num}.txt"

  cat test$num.txt | python grove.py | %{$_ -replace "Grove>> ", ""} > mine$num.txt
  diff (cat answer$num.txt) (cat mine$num.txt)
}
