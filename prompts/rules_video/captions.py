import json, os, zipfile
S="/tmp/claude-0/-home-user-rea-video/aab4cb51-a7e7-52e6-85f6-17b473411a46/scratchpad"
items=json.load(open(f"{S}/daily_items.json"))
ROMAN=["I","II","III","IV","V","VI","VII","VIII","IX","X"]
TAGS={1:"#Silence #MoveInSilence #Stoicism",2:"#ReadPeople #HumanNature #BodyLanguage",3:"#NeverChase #KnowYourWorth #SelfRespect",
4:"#RedFlags #FakeFriends #Boundaries",5:"#Respect #SelfRespect #Boundaries",6:"#EyeContact #BodyLanguage #Confidence",
7:"#NiceGuy #PeoplePleaser #Boundaries",8:"#SmallCircle #RealFriends #Loyalty",9:"#Manipulation #RedFlags #ToxicPeople",
10:"#Mystery #Privacy #MoveInSilence",11:"#Money #Friendship #FinancialWisdom",12:"#Composure #EmotionalControl #Stoicism",
13:"#QuietMan #Introvert #Stoicism",14:"#Negotiation #Business #Entrepreneur",15:"#Loyalty #FakeFriends #Friendship",
16:"#Presence #BodyLanguage #Confidence",17:"#Jealousy #Envy #Growth",18:"#MoveInSilence #Goals #Discipline",
19:"#SayNo #Boundaries #PeoplePleaser",20:"#HumanNature #LawsOfHumanNature #LifeLessons"}
OPEN=["Read it twice. Then read the room.","Most people learn this the hard way.","Simple to read. Hard to live.",
"Write this one down.","Nobody teaches this in school.","Some lessons cost years. This one is free.",
"Quiet truth for loud times.","Save this for the day you need it.","The ones who know, know.",
"Underline this. Live it.","Small rule. Big difference.","Hard to hear. Easy to prove.",
"Remember this the next time it happens.","This one separates boys from men.","Read slowly.",
"Learned it late? Teach it early.","The quiet ones already know this.","One page. One rule. Every day.",
"This changes how you see people.","Keep this one close."]
ASK=["Agree or disagree? 👇","Which part hit you hardest? 👇","Have you lived this? 👇","Who needs to read this today? Tag them. 👇",
"Did you learn this the hard way? 👇","Rate this rule from 1 to 10. 👇","True or false? 👇","What would you add? 👇",
"Save it, share it, live it. 📌","Be honest: do you follow this one? 👇"]
out=[]
for it in items:
    d=it["day"]
    cap=(f"{OPEN[(d-1)%len(OPEN)]}\n\n"
         f"“{it['text']}”\n\n"
         f"{it['topic']}, Rule {ROMAN[it['rule']-1]} 📖\n"
         f"{ASK[(d*7)%len(ASK)]}\n\n"
         f"Follow The Silent Code for one rule every day.\n"
         f"#TheSilentCode {TAGS[it['video']]} #DarkPsychology #Mindset #SelfImprovement")
    it["caption"]=cap; out.append(it)
    open(f"{S}/daily/day{d:03d}.txt","w").write(cap+"\n")
with open(f"{S}/daily/ALL_CAPTIONS.txt","w") as f:
    f.write("THE SILENT CODE: 200 DAILY PICTURE POSTS\nPost dayNNN.jpg with the caption under its day. Works on Facebook, Instagram, TikTok photo posts, X and Threads.\n\n")
    for it in out: f.write(f"==================== DAY {it['day']:03d}  ({it['file']}) ====================\n{it['caption']}\n\n")
z="/home/user/rea-video/prompts/TheSilentCode_200_daily_posts.zip"
with zipfile.ZipFile(z,"w",zipfile.ZIP_STORED) as zf:
    zf.write(f"{S}/daily/ALL_CAPTIONS.txt","TheSilentCode_daily_posts/ALL_CAPTIONS.txt")
    for it in out:
        zf.write(f"{S}/daily/{it['file']}",f"TheSilentCode_daily_posts/{it['file']}")
        zf.write(f"{S}/daily/day{it['day']:03d}.txt",f"TheSilentCode_daily_posts/day{it['day']:03d}.txt")
print(out[0]["caption"]); print(os.path.getsize(z)//1000000,"MB")
