#!/bin/bash
cd /home/user/rea-video/silent_code
python3 gen.py a1/scenes.json a1/kf b2 b3 b4 b5 b6 > a1/gen2.log 2>&1
python3 mouths.py a1/kf/avatar_501.png a1/landmarks.json a1/mouths > a1/mouths.log 2>&1
echo done > a1/assets.done
