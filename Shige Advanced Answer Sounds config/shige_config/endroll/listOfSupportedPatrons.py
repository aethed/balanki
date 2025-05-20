
from ..patrons_list import PATRONS_LIST
patrons_list = PATRONS_LIST.replace(",", "<br>")

ADDON_NAME = "🎧Advanced Answer Sounds" #🟢
CREATE_OR_FIXED = "Fixed by" #🟢

def clink(name, text,url=None):
    if not url:
        return f'{name} : {text}<br>'
    return f'{name} : <a href="{url}">{text}</a><br>'

credits = """
<br><br><br>
<b>[ CREDIT ]</b>
<br><br><br>
""".replace('\n', '<br>')

patreon = """
Special Thanks
<b>[ PATRONS ]</b>
{patrons_list}
""".format(patrons_list=patrons_list).replace('\n', '<br>')

sound =("<b>[ SOUNDS & BGM ]</b><br>"+
clink("Sound Effect", "Koukaon lab","https://soundeffect-lab.info/",)+
clink("Music" , "MaouDamashii","https://maou.audio/",)+
clink("Catgirl Voice","Cici Fyre","https://cicifyre.itch.io/")+
clink("Robot Voice","Charlie Pennell Productions©","https://www.charliepennellproductions.com/")+
clink("classical music"," Bernd Krueger","http://www.piano-midi.de/")
)


caractor = ("<b>[ IMAGE&3D MATERIALS ]</b><br>" +
clink("Knight","rvros","https://rvros.itch.io/") +
clink("Hooded","Penzilla","https://penzilla.itch.io/")+
clink("CatGirl","(Unity-chan)Kanbayashi Yuko<br>© Unity Technologies Japan/UCL","https://unity-chan.com/contents/guideline/")+
clink("Monsters","RPG dot(R-do) monta!","http://rpgdot3319.g1.xrea.com/")+
clink("Sushi","Ichika","https://www.ac-illust.com/main/profile.php?id=23341701&area=1")+
clink("Textures","PiiiXL","https://piiixl.itch.io/")+
clink("Banner Materials,Lock on cursor<br>","Nanamiyuki's Atelier","https://nanamiyuki.com/")+
clink("Sniper animated","DJMaesen","https://sketchfab.com/3d-models/sniper-animated-eae1ba5b43ae4bc89b0647fb5d8a2d27")+
clink("Parasite Zombie","Mixamo","https://www.mixamo.com/")+
clink("MiniZombie&RedHat","Fkgcluster","https://fkgcluster.itch.io/survivaltowerdefense")+
clink("BloodEffect","XYEzawr","https://xyezawr.itch.io/gif-free-pixel-effects-pack-5-blood-effects")+
clink("Cats","girlypixels","https://girlypixels.itch.io/")+
clink("Terminator-Core","Fred Drabble","https://sketchfab.com/3d-models/fusion-core-f717683d5502496d9e1ef1f1e1d1cb45" )+
clink("Terminator-Robo","Threedee","https://www.threedee.design/cartoon-robot")+
clink("Meowknight","9E0", "https://9e0.itch.io/")+
clink("Vegetable","Butter Milk","https://butterymilk.itch.io/")+
clink("Flower","kathychow","https://kathychow.itch.io/")+
clink("Crops", "bluecarrot16, Daniel Eddeland (daneeklu),<br> Joshua Taylor, Richard Kettering (Jetrel).<br> Commissioned by castelonia", "https://opengameart.org/content/lpc-crops")+
clink("Farmer","Butter Milk","https://butterymilk.itch.io/")

            )


addons = """<b>[ INSPIRED BY ADD-ONS ]</b>
Fanfare
Anki Habitica for 2.1
Life Drain
Progress Bar
Progress Bar original
Progress Bar, cards...
Speed Focus Mode
Hitmarkers
HUMBLE PIE

""".replace('\n', '<br>')

budle = ("<b>[ BUNDLE SOURCE CODE ]</b><br>"+
clink ("BGM","Pyglet","https://pyglet.readthedocs.io/en/latest/index.html")+
clink ("webp","dwebp","https://developers.google.com/speed/webp/download")+
clink ("midi","FluidSynth","https://www.fluidsynth.org/")

)

thankYou = ("""
<br><br><br>
<h3>%s</h3><br>""" % ADDON_NAME +
clink(f"{CREATE_OR_FIXED}", "Shigeyuki","https://www.patreon.com/Shigeyuki")+
"""
<br>
Thank you very much!
<br><br><br><br>
""")