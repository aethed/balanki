import os
import time
from typing import Tuple

from aqt import qt,gui_hooks
from aqt import mw
from aqt.qt import QAction,QFileInfo,QObject,QFileDialog
from aqt.qt import QUrl
from aqt.qt import qtmajor,QTimer
from aqt.utils import openFolder

from aqt.sound import *
from anki.sound import SoundOrVideoTag
from anki.cards import Card
from anki.utils import *

if qtmajor > 5:
    from PyQt6 import QtCore, QtGui, QtWidgets
    from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
else:
    from PyQt5 import QtCore, QtGui, QtWidgets
    from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent


import random
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "simpleaudio"))
from .simpleaudio_for_linux.choice_simpleaudio import load_simpleaudio
load_simpleaudio()
from . import simpleaudio as sa

from .shige_config.popup_config import set_gui_hook_change_log
set_gui_hook_change_log()

config = mw.addonManager.getConfig(__name__)

addon_path = os.path.dirname(__file__)
user_files = os.path.join(addon_path, "user_files")
sound_name = ["again","hard","good","easy",
              "graduate","correct","error","suspended","user buried","sched buried",
              "finish deck","delay question","delay answer",
              "fadein question","fadein answer",
              "ambient review","ambient menu",
              ]
#create sounds to wave_objs and store in sound_name list
sound_objs = {}
for i in range(0,len(sound_name)):
    if sound_name[i] in ["fadein question","fadein answer"]:
        continue
    sound_dir = os.path.join(user_files, sound_name[i])
    waves = []
    (root, dirs, files) = next(os.walk(sound_dir))
    for fileName in files:
        fileInfo = QFileInfo(fileName)
        fileExt = fileInfo.suffix().lower()
        if sound_name[i] in ["ambient review","ambient menu"]:
            if qtmajor > 5:
                if fileExt in ["wav",'mp3','aac','wma','flac']:
                    waves.append(os.path.join(sound_dir, fileName))
            else:
                if fileExt in ["wav",'mp3','wma']:
                    waves.append(os.path.join(sound_dir, fileName))
        elif fileExt == 'wav':
            if sound_name[i] in ["delay question","delay answer"]:
                waves.append(os.path.join(sound_dir, fileName))
            else:
                waves.append(sa.WaveObject.from_wave_file(os.path.join(sound_dir, fileName)))
    sound_objs[sound_name[i]] = waves

extra_ambient = []
# if config["ambient menu"]['paths']:
for path in config["ambient menu"]['paths']:
    extra_ambient.append(("ambient menu",path))
# if config["ambient review"]['path']:
for path in config["ambient review"]['paths']:
    extra_ambient.append(("ambient review",path))

def extent_extra_ambient(extras):
    for extra in extras:
        waves = []
        for root, _, files in os.walk(extra[1]):
            for fileName in files:
                fileInfo = QFileInfo(fileName)
                fileExt = fileInfo.suffix().lower()
                if qtmajor > 5:
                    if fileExt in ["wav",'mp3','aac','wma','flac']:
                        waves.append(os.path.join(root, fileName))
                else:
                    if fileExt in ["wav",'mp3','wma']:
                        waves.append(os.path.join(root, fileName))
        # sound_objs[extra[0]].extend(waves)
        for wave in waves:
            if wave not in sound_objs[extra[0]]:
                sound_objs[extra[0]].append(wave) 

extent_extra_ambient(extra_ambient)

class LoopSound(QObject):
    def __init__(self,name):
        super().__init__(mw)
        self.ambientName = name
        self.loopNames = sound_objs[name]
        self.volume = int(config[self.ambientName]["volume"])

        self.usedNames = []
        self.randNames = random.sample(self.loopNames,len(self.loopNames))

        self.player = QMediaPlayer()
        if qtmajor > 5:
            self.audio_output = QAudioOutput()
            self.player.setAudioOutput(self.audio_output)

        self.player.mediaStatusChanged.connect(self.statusChanged)
    
    def update(self):
        self.randNames = random.sample(self.loopNames,len(self.loopNames))

    def getNext(self) -> str:
        if not self.loopNames:
            return ""

        self.loopNames.append(self.loopNames.pop(0))
        return self.loopNames[-1]

    def getRandom(self):
        if len(self.loopNames) < 3:
            return random.choice(self.loopNames)

        if len(self.randNames)>1:
            self.usedNames.append(self.randNames[0])
            return self.randNames.pop(0)
        
        if self.usedNames:
            self.randNames.extend(random.sample(self.usedNames,len(self.usedNames)))
            self.randNames.insert(random.randrange(2,len(self.usedNames)+1),self.randNames[0])
            self.usedNames.clear()
        
        return self.randNames.pop(0)
    
    def statusChanged(self, status):
        if qtmajor > 5:
            if status == QMediaPlayer.MediaStatus.EndOfMedia:
                if config[self.ambientName]['mode'] == 'single':
                    mw.progress.single_shot(0, lambda: self.player.setSource(self.player.source()))
                elif config[self.ambientName]['mode'] == 'sequence':
                    mw.progress.single_shot(0, lambda: self.player.setSource(QUrl.fromLocalFile(self.getNext())))
                else:
                    mw.progress.single_shot(0, lambda: self.player.setSource(QUrl.fromLocalFile(self.getRandom())))
            elif status == QMediaPlayer.MediaStatus.LoadedMedia:
                if self.player.playbackState() == QMediaPlayer.PlaybackState.StoppedState:
                    mw.progress.single_shot(0, lambda: self.player.play())
        else:
            if status == QMediaPlayer.EndOfMedia:
                if config[self.ambientName]['mode'] == 'single':
                    mw.progress.single_shot(0, lambda: self.player.setMedia(self.player.media()))
                elif config[self.ambientName]['mode'] == 'sequence':
                    mw.progress.single_shot(0, lambda: self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.getNext()))))
                else:
                    mw.progress.single_shot(0, lambda: self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.getRandom()))))
            elif status == QMediaPlayer.LoadedMedia:
                if self.player.state() == QMediaPlayer.StoppedState:
                    mw.progress.single_shot(0, lambda: self.player.play())

    def play(self):
        if len(self.loopNames) == 0:
            return
        if qtmajor > 5:
            playState = self.player.playbackState()
            if playState == QMediaPlayer.PlaybackState.PlayingState:
                return
            if playState == QMediaPlayer.PlaybackState.PausedState:
                return self.player.play()
                
            self.setVolume(self.volume)
            if config[self.ambientName]['mode'] == 'sequence':
                self.player.setSource(QUrl.fromLocalFile(self.getNext()))
            else:
                self.player.setSource(QUrl.fromLocalFile(self.getRandom()))
        else:
            playState = self.player.state()
            if playState == QMediaPlayer.PlayingState:
                return
            if playState == QMediaPlayer.PausedState:
                return self.player.play()
                
            self.setVolume(self.volume)
            if config[self.ambientName]['mode'] == 'sequence':
                self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.getNext())))
            else:
                self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.getRandom())))
    
    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()
        time.sleep(0.1)

    def setVolume(self,volume):
        if volume < 0:
            volume = 0
        elif volume > 100:
            volume = 100
        self.volume = volume
        if qtmajor > 5:
            self.audio_output.setVolume(self.volume/100)
        else:
            self.player.setVolume(self.volume)

        config[self.ambientName]["volume"] = self.volume
        mw.addonManager.writeConfig(__name__,config)

reviewLooper = LoopSound("ambient review")
menuLooper = LoopSound("ambient menu")

class PlayObjWaiter(QObject):
    def __init__(self):
        super().__init__(mw)
        self.msec = 600
        self.playObj = None
        self.objName = None
        self.looper = None
        self.playTimer = QTimer()
        self.playTimer.timeout.connect(self.waitedCheck)

    def waitedCheck(self):
        if self.playObj and isinstance(self.playObj,sa.WaveObject):
            self.playObj = self.playObj.play(config[self.objName]['volume'])
            return
        if self.playObj and self.playObj.is_playing():
            return

        self.playObj = None
        if config['ambient menu']['enable'] == 1:
            self.looper.play()
        else:
            self.looper.pause() 

        self.playTimer.stop()

    def play(self):
        self.playTimer.stop()
        if self.playObj:
            return self.playTimer.start(self.msec)

        if config['ambient menu']['enable'] == 1:
            self.looper.play()

    def pause(self):
        self.playTimer.stop()
        self.playObj = None
        self.looper.pause()

menuPlayer = PlayObjWaiter()
menuPlayer.looper = menuLooper

# store some info
last_card = None

play_cloz = None
play_easy = None    
play_grad = None 
play_opt = None

# create fade in for play sounds to delay question and answer avtag
from aqt.reviewer import Reviewer
from typing import Any, Optional, Tuple

def on_webview(web_content: aqt.webview.WebContent, context: Optional[Any]) -> None:
    if isinstance(context, Reviewer):
        web_content.head += "<style> body { opacity: 0; transition: opacity 1s;} </style>"
gui_hooks.webview_will_set_content.append(on_webview)

def card_will_show(txt: str, card: Card, kind: str) -> str:
    mw.web.eval(f"document.body.style.opacity=0.0;document.body.style.transition='opacity 0s';")
    return txt
gui_hooks.card_will_show.append(card_will_show)

def card_will_fadein(kind: str):
    span = "0"
    if int(config[kind]["enable"]) == 1:
        span = config[kind]['time']
    mw.web.eval(f"document.body.style.opacity=1.0;document.body.style.transition='opacity {span}s ease-in';")

gui_hooks.reviewer_did_show_question.append(lambda c:  card_will_fadein("fadein question"))
gui_hooks.reviewer_did_show_answer.append(lambda c:  card_will_fadein("fadein answer"))


# play for ease and graduate:
easytypes = [0,1,2,3,4,5,6,7,8,9]
easynames = ["none","again","hard","good","easy","easy","easy","easy","easy","easy"]
def reviewer_will_init_answer_buttons(buttons_tuple: Tuple[Tuple[int, str], ...], val2, val3) -> Tuple[Tuple[int, str], ...]:
    global easytypes
    button_count = len(buttons_tuple)
    if button_count == 2:
        easytypes = [0,1,3]
    elif button_count == 3:
        easytypes = [0,1,3,4]
    elif button_count == 4:
        easytypes = [0,1,2,3,4]
    else:
        easytypes = [0,1,2,3,4,5,6,7,8,9] #for safe

    return buttons_tuple	
gui_hooks.reviewer_will_init_answer_buttons.append(reviewer_will_init_answer_buttons)

origin_queue = None
def reviewer_did_show_answer(c):
    global origin_queue
    origin_queue = c.queue
    
gui_hooks.reviewer_did_show_answer.append(reviewer_did_show_answer)

# play for ease and graduate:
def reviewer_will_answer_card(ease_tuple: Tuple[bool, int], reviewer, card: Card) -> Tuple[bool, int]:
    global play_easy
    # for ease_type
    mytype = easytypes[ease_tuple[1]]
    myname = easynames[mytype]
    if int(config[myname]["enable"]) == 1 and sound_objs[myname]:
        play_easy = random.choice(sound_objs[myname]).play(config[myname]['volume'])

    return ease_tuple

gui_hooks.reviewer_will_answer_card.append(reviewer_will_answer_card)


# play for graduate and try wait easy sometime
delay_time = 0.0
def grad_wait_ease_play():
    global delay_time, play_easy,play_grad
    if delay_time <= float(config["graduate"]["wait_ease"]) and play_easy and play_easy.is_playing():
        mw.progress.single_shot(100, lambda: grad_wait_ease_play())
        delay_time += 0.1
        return
    if play_grad and isinstance(play_grad,sa.WaveObject):
        play_grad = play_grad.play(config["graduate"]['volume'])

def reviewer_did_answer_card(self, card, ease):
    global origin_queue,play_grad,delay_time
    # for graduate: not invoke play() wait for ease judge
    if int(config["graduate"]["enable"]) == 1 and card.queue == 2 and (origin_queue == 0 or origin_queue == 1) and sound_objs["graduate"]:
        delay_time = 0.0 
        play_grad = random.choice(sound_objs["graduate"])
        if float(config["graduate"]["wait_ease"]) > 0.0:
            mw.progress.single_shot(0, lambda: grad_wait_ease_play())
        else:
            play_grad = play_grad.play(config["graduate"]['volume'])

    return

    
gui_hooks.reviewer_did_answer_card.append(reviewer_did_answer_card)

# play for opts: suspend buriy
def reviewer_will_play_opt_sounds(bc):
    opt_name = ""
    try:
        bc.load()
        if bc.queue == -1:
            opt_name = 'suspended'
        elif bc.queue == -2:
            opt_name = 'user buried'
        elif bc.queue == -3: 
            opt_name = 'sched buried'
    except:
        pass

    global play_opt
    if opt_name != "" and int(config[opt_name]["enable"]) == 1 and sound_objs[opt_name]:
        play_opt = random.choice(sound_objs[opt_name]).play(config[opt_name]['volume'])

def reviewer_will_play_question_sounds(c, sounds):
    global last_card    
    if last_card:
        reviewer_will_play_opt_sounds(last_card)
    last_card = c


def reviewer_will_end():
    global last_card    
    if last_card:
        reviewer_will_play_opt_sounds(last_card)
    last_card = None

gui_hooks.reviewer_will_play_question_sounds.append(reviewer_will_play_question_sounds)
gui_hooks.reviewer_will_end.append(reviewer_will_end)

# for delay question and answer
def av_player_will_play_tags(sounds, state, self):
    if len(sounds) == 0:
        return
    delay_name = "delay question" if state == "question" else "delay answer"

    if int(config[delay_name]["enable"]) == 0:
        return

    tag = SoundOrVideoTag(sound_objs[delay_name][0])
    for i in range(0,int(float(config[delay_name]["time"])/0.5)):
        sounds.insert(0,tag)
    return

gui_hooks.av_player_will_play_tags.append(av_player_will_play_tags)

# after sounds insert need to remove for replay
def remove_delayed_sounds(sounds):
    for i in range(len(sounds)-1, -1, -1):
        if hasattr(sounds[i], 'filename') and sounds[i].filename.find(user_files) != -1:
            sounds.pop(i)

gui_hooks.reviewer_did_show_question.append(lambda c: remove_delayed_sounds(c.question_av_tags()))
gui_hooks.reviewer_did_show_answer.append(lambda c: remove_delayed_sounds(c.answer_av_tags()))

def state_did_change(new_state, old_state):
    if new_state == "review":
        menuPlayer.pause()
        if config['ambient review']['enable'] == 1:
            reviewLooper.play()

    if new_state == "overview":
        reviewLooper.pause()
        menuPlayer.pause()

        opt_name = "finish deck"
        if mw.col.sched.get_queued_cards().cards:
            menuPlayer.play()
        else:
            if int(config[opt_name]["enable"]) == 1 and sound_objs[opt_name]:
                menuPlayer.playObj = random.choice(sound_objs[opt_name])
                menuPlayer.objName = opt_name
            else:
                menuPlayer.playObj = None
            menuPlayer.play()

    if new_state == "deckBrowser":
        reviewLooper.pause()
        menuPlayer.pause()

        menuPlayer.play()

    return
gui_hooks.state_did_change.append(state_did_change)

def reviewer_did_show_question(card):
    if card and card != mw.reviewer.card:
        return

    if config['ambient review']['enable'] == 1:
        if config['ambient review']['continue'] == 0 and mw.reviewer.state == "question":
            reviewLooper.stop()
            reviewLooper.play()

gui_hooks.reviewer_did_show_question.append(reviewer_did_show_question)

# for type Cloze
def type_error_beep(text):
    if int(config["error"]["enable"]) != 1:
        return

    if text.find("<span class=typeBad>") != -1 or text.find("<span class=typeMissed>") != -1 :
        obj_name = "error"
    elif text.find("<span class=typeGood>") != -1 :
        obj_name = "correct"
    else:
        return

    global play_cloz
    if sound_objs[obj_name]:
        play_cloz = random.choice(sound_objs[obj_name]).play(config[obj_name]['volume'])

    return

def reviewer_will_play_answer_sounds(c, sounds):
    old_typebox_note = None
    if hasattr(mw.reviewer, "_typebox_note"):
        old_typebox_note = mw.reviewer._typebox_note

    a = c.answer()
    a = mw.reviewer._mungeQA(a)
    type_error_beep(a)
    if old_typebox_note != None:
        mw.reviewer._typebox_note = old_typebox_note

gui_hooks.reviewer_will_play_answer_sounds.append(reviewer_will_play_answer_sounds)



class FolderList(qt.QDialog):
    def __init__(self,player:LoopSound):
        qt.QDialog.__init__(self, mw)
        self.player = player
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 400, 300)

        main_layout = qt.QVBoxLayout()
        self.folder_list = qt.QListWidget()
        main_layout.addWidget(self.folder_list)

        button_layout = qt.QHBoxLayout()
        add_button = qt.QPushButton('add folder')
        add_button.clicked.connect(self.add_folder)
        button_layout.addWidget(add_button)

        remove_button = qt.QPushButton('del folder')
        remove_button.clicked.connect(self.remove_folder)
        button_layout.addWidget(remove_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def add_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'select dir')
        if folder_path:
            self.folder_list.addItem(folder_path)
            extent_extra_ambient([(self.player.ambientName,folder_path)])

            config[self.player.ambientName]['paths'].append(folder_path)
            mw.addonManager.writeConfig(__name__,config)

            self.player.update()

    def remove_folder(self):
        selected_item = self.folder_list.currentItem()
        if selected_item:
            self.folder_list.takeItem(self.folder_list.row(selected_item))

            config[self.player.ambientName]['paths'].remove(selected_item.text())
            mw.addonManager.writeConfig(__name__,config)


class ConfigDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self, mw)
        if qtmajor > 5:
            from . import sound
            self.form = sound.Ui_Dialog()
        else:
            from . import sound_qt5
            self.form = sound_qt5.Ui_Dialog()
        self.form.setupUi(self)

        self.form.checkBoxAgain.stateChanged.connect(self.on_checkbox_changed_again)
        self.form.checkBoxHard.stateChanged.connect(self.on_checkbox_changed_hard)
        self.form.checkBoxGood.stateChanged.connect(self.on_checkbox_changed_good)
        self.form.checkBoxEasy.stateChanged.connect(self.on_checkbox_changed_easy)
        self.form.checkBoxGrad.stateChanged.connect(self.on_checkbox_changed_grad)
        self.form.spinGradWaitEasy.valueChanged.connect(self.spin_grad_wait)
        self.form.checkBoxFinish.stateChanged.connect(self.on_checkbox_changed_finish)

        self.form.checkBoxCorrect.stateChanged.connect(self.on_checkbox_changed_correct)
        self.form.checkBoxError.stateChanged.connect(self.on_checkbox_changed_error)

        self.form.checkBoxSuspended.stateChanged.connect(self.on_checkbox_changed_suspended)
        self.form.checkBoxBuriedUsr.stateChanged.connect(self.on_checkbox_changed_buried_usr)
        self.form.checkBoxBuriedSch.stateChanged.connect(self.on_checkbox_changed_buried_sch)

        self.form.spinBoxVolAgain.valueChanged.connect(self.spin_vol_again)
        self.form.spinBoxVolHard.valueChanged.connect(self.spin_vol_hard)
        self.form.spinBoxVolGood.valueChanged.connect(self.spin_vol_good)
        self.form.spinBoxVolEasy.valueChanged.connect(self.spin_vol_easy)
        self.form.spinBoxVolGraduate.valueChanged.connect(self.spin_vol_graduate)
        self.form.spinBoxVolFinish.valueChanged.connect(self.spin_vol_finish)
        self.form.spinBoxVolCorret.valueChanged.connect(self.spin_vol_correct)
        self.form.spinBoxVolError.valueChanged.connect(self.spin_vol_error)
        self.form.spinBoxVolSuspended.valueChanged.connect(self.spin_vol_suspended)
        self.form.spinBoxVolBuriedUsr.valueChanged.connect(self.spin_vol_buried_usr)
        self.form.spinBoxVolBuriedSch.valueChanged.connect(self.spin_vol_buried_sch)

        self.form.checkBoxDelayQ.stateChanged.connect(self.on_checkbox_changed_delay_q)
        self.form.spinDelayQ.valueChanged.connect(self.spin_delay_q)
        self.form.checkBoxDelayA.stateChanged.connect(self.on_checkbox_changed_delay_a)
        self.form.spinDelayA.valueChanged.connect(self.spin_delay_a)

        self.form.checkBoxFadeInQ.stateChanged.connect(self.on_checkbox_changed_fadein_q)
        self.form.spinFadeInQ.valueChanged.connect(self.spin_fadein_q)
        self.form.checkBoxFadeInA.stateChanged.connect(self.on_checkbox_changed_fadein_a)
        self.form.spinFadeInA.valueChanged.connect(self.spin_fadein_a)

        self.form.checkBoxAmbientM.stateChanged.connect(self.on_checkbox_changed_AM)
        self.form.sliderAmbientMVol.valueChanged.connect(self.adjAMVolume)
        self.form.comboBoxAmbientMMode.addItem("random")
        self.form.comboBoxAmbientMMode.addItem("single")
        self.form.comboBoxAmbientMMode.addItem("sequence")
        if config["ambient menu"]["mode"] == "random":
            self.form.comboBoxAmbientMMode.setCurrentIndex(0)
        elif config["ambient menu"]["mode"] == "single":
            self.form.comboBoxAmbientMMode.setCurrentIndex(1)
        elif config["ambient menu"]["mode"] == "sequence":
            self.form.comboBoxAmbientMMode.setCurrentIndex(2)
        else:
            self.form.comboBoxAmbientMMode.setCurrentIndex(0)
        self.form.comboBoxAmbientMMode.currentIndexChanged.connect(lambda idx: self.index_change_mode(idx, "ambient menu"))

        self.form.checkBoxAmbientR.stateChanged.connect(self.on_checkbox_changed_AR)
        self.form.sliderAmbientRVol.valueChanged.connect(self.adjARVolume)
        self.form.checkBoxAmbientRContinue.stateChanged.connect(self.on_checkbox_changed_ARC)
        self.form.comboBoxAmbientRMode.addItem("random")
        self.form.comboBoxAmbientRMode.addItem("single")
        self.form.comboBoxAmbientRMode.addItem("sequence")
        if config["ambient review"]["mode"] == "random":
            self.form.comboBoxAmbientRMode.setCurrentIndex(0)
        elif config["ambient review"]["mode"] == "single":
            self.form.comboBoxAmbientRMode.setCurrentIndex(1)
        elif config["ambient review"]["mode"] == "sequence":
            self.form.comboBoxAmbientRMode.setCurrentIndex(2)
        else:
            self.form.comboBoxAmbientRMode.setCurrentIndex(0)
        self.form.comboBoxAmbientRMode.currentIndexChanged.connect(lambda idx: self.index_change_mode(idx, "ambient review"))

        self.form.pushButtonPathMenu.clicked.connect(self.on_select_menu_path)
        self.form.pushButtonPathReview.clicked.connect(self.on_select_review_path)

        self.init_ui()

        from .shige_tools.button_manager import mini_button
        from aqt.utils import openLink
        ADDON_PACKAGE = mw.addonManager.addonFromModule(__name__)

        userFilesButton = QtWidgets.QPushButton("📂UserFiles", self)
        mini_button(userFilesButton)
        user_files = os.path.join(os.path.dirname(__file__), "user_files")
        # userFilesButton.clicked.connect(lambda: os.startfile(user_files))
        userFilesButton.clicked.connect(lambda: openFolder(user_files))

        rateThisButton = QtWidgets.QPushButton("👍️RateThis", self)
        mini_button(rateThisButton)
        rateThisButton.clicked.connect(lambda: openLink(f"https://ankiweb.net/shared/review/{ADDON_PACKAGE}"))

        patreonButton = QtWidgets.QPushButton("💖Patreon", self)
        mini_button(patreonButton)
        patreonButton.clicked.connect(lambda: openLink("http://patreon.com/Shigeyuki"))

        wikiButton = QtWidgets.QPushButton("📖Wiki", self)
        mini_button(wikiButton)
        wikiButton.clicked.connect(lambda: openLink("https://shigeyukey.github.io/shige-addons-wiki/advanced-answer-sound.html"))

        reportButton = QtWidgets.QPushButton("🚨Report", self)
        mini_button(reportButton)
        reportButton.clicked.connect(lambda: openLink("https://shigeyukey.github.io/shige-addons-wiki/advanced-answer-sound.html#report"))

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setGeometry(QtCore.QRect(0, 540, 400, 50))

        hboxLayout = QtWidgets.QHBoxLayout(layoutWidget)
        hboxLayout.addWidget(userFilesButton)
        hboxLayout.addWidget(wikiButton)
        hboxLayout.addWidget(reportButton)
        hboxLayout.addWidget(rateThisButton)
        hboxLayout.addWidget(patreonButton)

        hboxLayout.addStretch()




    def init_ui(self):

        self.form.checkBoxAgain.setChecked(config["again"]['enable'])
        self.form.checkBoxHard.setChecked(config["hard"]['enable'])
        self.form.checkBoxGood.setChecked(config["good"]['enable'])
        self.form.checkBoxEasy.setChecked(config["easy"]['enable'])
        self.form.checkBoxGrad.setChecked(config["graduate"]['enable'])
        self.form.spinGradWaitEasy.setValue(float(config["graduate"]['wait_ease']))
        self.form.checkBoxFinish.setChecked(config["finish deck"]['enable'])

        self.form.checkBoxCorrect.setChecked(config["correct"]['enable'])
        self.form.checkBoxError.setChecked(config["error"]['enable'])

        self.form.checkBoxSuspended.setChecked(config["suspended"]['enable'])
        self.form.checkBoxBuriedUsr.setChecked(config["user buried"]['enable'])
        self.form.checkBoxBuriedSch.setChecked(config["sched buried"]['enable'])

        self.form.spinBoxVolAgain.setValue(int(config["again"]['volume']))
        self.form.spinBoxVolHard.setValue(int(config["hard"]['volume']))
        self.form.spinBoxVolGood.setValue(int(config["good"]['volume']))
        self.form.spinBoxVolEasy.setValue(int(config["easy"]['volume']))
        self.form.spinBoxVolGraduate.setValue(int(config["graduate"]['volume']))
        self.form.spinBoxVolCorret.setValue(int(config["correct"]['volume']))
        self.form.spinBoxVolError.setValue(int(config["error"]['volume']))
        self.form.spinBoxVolFinish.setValue(int(config["finish deck"]['volume']))
        self.form.spinBoxVolSuspended.setValue(int(config["suspended"]['volume']))
        self.form.spinBoxVolBuriedUsr.setValue(int(config["user buried"]['volume']))
        self.form.spinBoxVolBuriedSch.setValue(int(config["sched buried"]['volume']))

        self.form.checkBoxDelayQ.setChecked(config["delay question"]['enable'])
        self.form.spinDelayQ.setValue(float(config["delay question"]['time']))
        self.form.checkBoxDelayA.setChecked(config["delay answer"]['enable'])
        self.form.spinDelayA.setValue(float(config["delay answer"]['time']))

        self.form.checkBoxFadeInQ.setChecked(config["fadein question"]['enable'])
        self.form.spinFadeInQ.setValue(float(config["fadein question"]['time']))
        self.form.checkBoxFadeInA.setChecked(config["fadein answer"]['enable'])
        self.form.spinFadeInA.setValue(float(config["fadein answer"]['time']))

        self.form.checkBoxAmbientM.setChecked(config["ambient menu"]['enable'])
        self.form.sliderAmbientMVol.setValue(config["ambient menu"]['volume'])

        self.form.checkBoxAmbientR.setChecked(config["ambient review"]['enable'])
        self.form.sliderAmbientRVol.setValue(config["ambient review"]['volume'])
        self.form.checkBoxAmbientRContinue.setChecked(config["ambient review"]['continue'])

    def on_select_menu_path(self):  
        oDlg = FolderList(menuLooper)
        oDlg.setWindowTitle('Ambient menu music extra folders')
        for path in config["ambient menu"]['paths']:
            oDlg.folder_list.addItem(path)
        oDlg.exec()
        # dir_choose = QFileDialog.getExistingDirectory(self, "select dir", os.path.join(user_files, "ambient menu"))
        # if dir_choose == "":
        #     return
        # extent_extra_ambient([("ambient menu",dir_choose)])

        # self.form.lineEditPathMenu.setText(dir_choose)
        # config["ambient menu"]['path'] = dir_choose
        # mw.addonManager.writeConfig(__name__,config)

        # menuLooper.update()

    def on_select_review_path(self):
        oDlg = FolderList(reviewLooper)
        oDlg.setWindowTitle('Ambient review music extra folders')
        for path in config["ambient review"]['paths']:
            oDlg.folder_list.addItem(path)
        oDlg.exec()

    def on_checkbox_changed_again(self, value):
        config["again"]['enable'] = True if Qt.CheckState(value) == Qt.CheckState.Checked else False
        mw.addonManager.writeConfig(__name__,config)
    def on_checkbox_changed_hard(self, value):
        config["hard"]['enable'] = True if Qt.CheckState(value) == Qt.CheckState.Checked else False
        mw.addonManager.writeConfig(__name__,config)
    def on_checkbox_changed_good(self, value):
        config["good"]['enable'] = True if Qt.CheckState(value) == Qt.CheckState.Checked else False
        mw.addonManager.writeConfig(__name__,config)
    def on_checkbox_changed_easy(self, value):
        config["easy"]['enable'] = True if Qt.CheckState(value) == Qt.CheckState.Checked else False
        mw.addonManager.writeConfig(__name__,config)
    def on_checkbox_changed_grad(self, value):
        config["graduate"]['enable'] = True if Qt.CheckState(value) == Qt.CheckState.Checked else False
        mw.addonManager.writeConfig(__name__,config)
    def spin_grad_wait(self):
        config["graduate"]['wait_ease'] = self.form.spinGradWaitEasy.value()
        mw.addonManager.writeConfig(__name__,config)
    def on_checkbox_changed_finish(self, value):
        config["finish deck"]['enable'] = True if Qt.CheckState(value) == Qt.CheckState.Checked else False
        mw.addonManager.writeConfig(__name__,config)

    def on_checkbox_changed_correct(self, value):
        config["correct"]['enable'] = True if Qt.CheckState(value) == Qt.CheckState.Checked else False
        mw.addonManager.writeConfig(__name__,config)
    def on_checkbox_changed_error(self, value):
        config["error"]['enable'] = True if Qt.CheckState(value) == Qt.CheckState.Checked else False
        mw.addonManager.writeConfig(__name__,config)

    def on_checkbox_changed_suspended(self, value):
        config["suspended"]['enable'] = True if Qt.CheckState(value) == Qt.CheckState.Checked else False
        mw.addonManager.writeConfig(__name__,config)
    def on_checkbox_changed_buried_usr(self, value):
        config["user buried"]['enable'] = True if Qt.CheckState(value) == Qt.CheckState.Checked else False
        mw.addonManager.writeConfig(__name__,config)
    def on_checkbox_changed_buried_sch(self, value):
        config["sched buried"]['enable'] = True if Qt.CheckState(value) == Qt.CheckState.Checked else False
        mw.addonManager.writeConfig(__name__,config)

    def on_checkbox_changed_delay_q(self, value):
        config["delay question"]['enable'] = True if Qt.CheckState(value) == Qt.CheckState.Checked else False
        mw.addonManager.writeConfig(__name__,config)
    def spin_delay_q(self):
        config["delay question"]['time'] = self.form.spinDelayQ.value()
        mw.addonManager.writeConfig(__name__,config)
    def on_checkbox_changed_delay_a(self, value):
        config["delay answer"]['enable'] = True if Qt.CheckState(value) == Qt.CheckState.Checked else False
        mw.addonManager.writeConfig(__name__,config)
    def spin_delay_a(self):
        config["delay answer"]['time'] = self.form.spinDelayA.value()
        mw.addonManager.writeConfig(__name__,config)

    def on_checkbox_changed_fadein_q(self, value):
        config["fadein question"]['enable'] = True if Qt.CheckState(value) == Qt.CheckState.Checked else False
        mw.addonManager.writeConfig(__name__,config)
    def spin_fadein_q(self):
        config["fadein question"]['time'] = round(self.form.spinFadeInQ.value(), 1)
        mw.addonManager.writeConfig(__name__,config)
    def on_checkbox_changed_fadein_a(self, value):
        config["fadein answer"]['enable'] = True if Qt.CheckState(value) == Qt.CheckState.Checked else False
        mw.addonManager.writeConfig(__name__,config)
    def spin_fadein_a(self):
        config["fadein answer"]['time'] = round(self.form.spinFadeInA.value(), 1)
        mw.addonManager.writeConfig(__name__,config)

    def on_checkbox_changed_AM(self, value):
        isEnabled = True if Qt.CheckState(value) == Qt.CheckState.Checked else False
        config["ambient menu"]['enable'] = isEnabled
        mw.addonManager.writeConfig(__name__,config)
        if mw.state == "deckBrowser" or mw.state == "overview":
            if isEnabled:
                menuLooper.play()
            else:
                menuLooper.pause()

    def on_checkbox_changed_AR(self, value):
        isEnabled = True if Qt.CheckState(value) == Qt.CheckState.Checked else False
        config["ambient review"]['enable'] = isEnabled
        mw.addonManager.writeConfig(__name__,config)
        if mw.state == "review":
            if isEnabled:
                reviewLooper.play()
            else:
                reviewLooper.pause()

    def on_checkbox_changed_ARC(self, value):
        config["ambient review"]['continue'] = True if Qt.CheckState(value) == Qt.CheckState.Checked else False
        mw.addonManager.writeConfig(__name__,config)

    def index_change_mode(self,i:int, name:str):
        if name == "ambient menu":
            config["ambient menu"]['mode'] = self.form.comboBoxAmbientMMode.itemText(i)
            mw.addonManager.writeConfig(__name__,config)
        elif name == "ambient review":
            config["ambient review"]['mode'] = self.form.comboBoxAmbientRMode.itemText(i)
            mw.addonManager.writeConfig(__name__,config)

    def adjAMVolume(self,val:int):
        menuLooper.setVolume(val)
        self.form.labelAmbientMVol.setText(f"{val}%")
        config["ambient menu"]['volume'] = val
        mw.addonManager.writeConfig(__name__,config)

    def adjARVolume(self,val:int):
        reviewLooper.setVolume(val)
        self.form.labelAmbientRVol.setText(f"{val}%")
        config["ambient review"]['volume'] = val
        mw.addonManager.writeConfig(__name__,config)

    def spin_vol_again(self):
        config["again"]['volume'] = self.form.spinBoxVolAgain.value()
        mw.addonManager.writeConfig(__name__,config)

    def spin_vol_hard(self):
        config["hard"]['volume'] = self.form.spinBoxVolHard.value()
        mw.addonManager.writeConfig(__name__,config)

    def spin_vol_good(self):
        config["good"]['volume'] = self.form.spinBoxVolGood.value()
        mw.addonManager.writeConfig(__name__,config)

    def spin_vol_easy(self):
        config["easy"]['volume'] = self.form.spinBoxVolEasy.value()
        mw.addonManager.writeConfig(__name__,config)

    def spin_vol_graduate(self):
        config["graduate"]['volume'] = self.form.spinBoxVolGraduate.value()
        mw.addonManager.writeConfig(__name__,config)

    def spin_vol_finish(self):
        config["finish deck"]['volume'] = self.form.spinBoxVolFinish.value()
        mw.addonManager.writeConfig(__name__,config)


    def spin_vol_correct(self):
        config["correct"]['volume'] = self.form.spinBoxVolCorret.value()
        mw.addonManager.writeConfig(__name__,config)


    def spin_vol_error(self):
        config["error"]['volume'] = self.form.spinBoxVolError.value()
        mw.addonManager.writeConfig(__name__,config)


    def spin_vol_suspended(self):
        config["suspended"]['volume'] = self.form.spinBoxVolSuspended.value()
        mw.addonManager.writeConfig(__name__,config)


    def spin_vol_buried_usr(self):
        config["user buried"]['volume'] = self.form.spinBoxVolBuriedUsr.value()
        mw.addonManager.writeConfig(__name__,config)


    def spin_vol_buried_sch(self):
        config["sched buried"]['volume'] = self.form.spinBoxVolBuriedSch.value()
        mw.addonManager.writeConfig(__name__,config)


def EffectConfig() -> None:
    dlg = ConfigDialog()
    dlg.exec()

action = QAction("🎧Advanced Answer Sounds (Fixed by Shigeඞ)", mw)
qconnect(action.triggered, EffectConfig)
mw.form.menuTools.addAction(action)
mw.addonManager.setConfigAction(__name__, EffectConfig)
