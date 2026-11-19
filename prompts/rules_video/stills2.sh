S=/tmp/claude-0/-home-user-rea-video/aab4cb51-a7e7-52e6-85f6-17b473411a46/scratchpad
cd $S && . venv/bin/activate
export REA_BG_CFG=$S/bg/cfg_a.json REA_FONTS=$S/fontpk/x_fontpkg_libre_baskerville-2.5-py3-none-any.whl/fontpkg_libre_baskerville/files
for n in $(seq 21 40); do
  t=$(python3 -c "import json;T=json.load(open('$S/v$n/timeline.json'));print(round(T['sent'][1]['t1']+0.2,2))")
  python v1/render2.py $S/v$n x --still $t > /dev/null 2>&1 && cp $S/v$n/still_$(printf %05.2f $t).png $S/v$n/cover_bg.png && echo "v$n ok"
done
