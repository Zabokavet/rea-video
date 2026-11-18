# usage: render_one.sh N   (expects vN/sents.json from voice+asr)
set -e
S=/tmp/claude-0/-home-user-rea-video/aab4cb51-a7e7-52e6-85f6-17b473411a46/scratchpad
n=${1%r}; WD=$S/v$n; OUTDIR=/home/user/rea-video/prompts/videos
mkdir -p $OUTDIR
cd $S && . venv/bin/activate
export REA_FONTS=$S/fontpk/x_fontpkg_libre_baskerville-2.5-py3-none-any.whl/fontpkg_libre_baskerville/files HF_HUB_DISABLE_PROGRESS_BARS=1
slug=$(python -c "import json;m=[x for x in json.load(open('$S/videos.json')) if x['n']==$n][0];print('video%02d_%s'%($n,m['slug']))")
rm -f $WD/timeline.json
python v1/render.py $WD x > $WD/layout.log 2>&1
python v1/timeline.py $WD > $WD/timeline.log 2>&1
python v1/audio.py $WD > $WD/audio.log 2>&1
if [ "$2" != "audio-only" ] || [ ! -f $WD/video_noaudio.mp4 ]; then
  python v1/render.py $WD $WD/video_noaudio.mp4 > $WD/render.log 2>&1
fi
ffmpeg -y -v error -i $WD/video_noaudio.mp4 -i $WD/mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -crf 20 -maxrate 9M -bufsize 18M -pix_fmt yuv420p -profile:v high -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest $OUTDIR/$slug.mp4
python v1/verify.py $WD $OUTDIR/$slug.mp4 2>/dev/null | grep -v -i warn | sed "s/^/v$n /"
rm -f $WD/seg0.mp4 $WD/seg1.mp4 $WD/seg2.mp4 $WD/seg3.mp4 $WD/mix_raw.f32 $WD/voice_raw.f32 $WD/voice_proc.f32 $WD/voice_only.f32 $WD/music_only.f32
echo "v$n DONE $slug"
