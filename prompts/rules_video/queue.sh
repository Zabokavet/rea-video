# renders every N listed in queue.txt once (append numbers to queue.txt to add work)
S=/tmp/claude-0/-home-user-rea-video/aab4cb51-a7e7-52e6-85f6-17b473411a46/scratchpad
touch $S/queue_done.txt
while true; do
  next=$(grep -vxFf $S/queue_done.txt $S/queue.txt | head -1)
  if [ -z "$next" ]; then
    if [ -f $S/queue_stop ]; then echo QUEUE_EMPTY; exit 0; fi
    sleep 5; continue
  fi
  bash $S/render_one.sh $next 2>&1 | grep -E "^v[0-9]+ |rror|Traceback" || echo "v$next FAILED"
  echo $next >> $S/queue_done.txt
done
