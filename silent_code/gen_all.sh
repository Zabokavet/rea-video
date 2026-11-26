#!/bin/bash
cd "$(dirname "$0")"
for r in r1 r2 r3 r4 r5; do python3 gen.py $r/shots.json $r/kf > $r/gen.log 2>&1; echo "$r done"; done
