from . import experimentalCardEaseFactor
from aqt import mw
if mw.addonManager.getConfig(__name__).get('two_button_mode'):
    from . import YesOrNo
