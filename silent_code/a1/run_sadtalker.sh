#!/bin/bash
# waits for scene generation, then animates the avatar (lip-sync, blinks, expressions)
cd /home/user/rea-video/silent_code
source ~/st-venv/bin/activate
cd ~/SadTalker
python inference.py --driven_audio /home/user/rea-video/silent_code/a1/avatar_audio.wav \
  --source_image /home/user/rea-video/silent_code/a1/kf/avatar_501.png --result_dir /home/user/rea-video/silent_code/a1/talk \
  --still --preprocess full --size 256 --expression_scale 1.25 --cpu > /home/user/rea-video/silent_code/a1/talk.log 2>&1
echo "sadtalker exit $?" >> /home/user/rea-video/silent_code/a1/talk.log
