bash scripts/run.sh >/tmp/user-output.txt
echo "<cx:tap>"
echo "TAP version 13"
echo "1..1"
if cmp /tmp/user-output.txt template-output.txt >/dev/null; then
  echo ok 1 - you are a genius
  OK=genius
else
  echo not ok 1 - maybe enroll at Winterthur?
  OK=Winterthur
fi
echo "</cx:tap>"
echo $OK
