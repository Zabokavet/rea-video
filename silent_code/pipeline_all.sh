#!/bin/bash
# after each reel's keyframes are done: build a contact sheet for review
cd "$(dirname "$0")"
for r in r1 r2 r3 r4 r5; do
  while ! grep -q "^$r done" gen_all.log; do sleep 20; done
  python3 -c "
from PIL import Image;import glob
fs=sorted(glob.glob('$r/kf/*.png'));ims=[Image.open(f).resize((256,448)) for f in fs]
cols=8;c=Image.new('RGB',(256*cols,448*((len(ims)+cols-1)//cols)))
[c.paste(im,((i%cols)*256,(i//cols)*448)) for i,im in enumerate(ims)];c.save('$r/contact.jpg')
print('$r', len(fs))"
done
