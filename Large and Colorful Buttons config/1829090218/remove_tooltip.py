# -*- coding: utf-8 -*-

from anki.hooks import addHook
from aqt import mw


config = mw.addonManager.getConfig(__name__)

if config.get('REMOVE_TOOLTIP'):

    js = '$("button").removeAttr("title");'

    # title属性を削除してボタンのツールチップを出ないようにする
    def remove_tooltip():
        mw.reviewer.bottom.web.eval(js)

    addHook('showQuestion', remove_tooltip)
    addHook('showAnswer', remove_tooltip)
