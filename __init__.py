from . import autoEaseFactor
from . import sync_hook
from aqt import mw
if mw.addonManager.getConfig(__name__).get('two_button_mode'):
    from . import YesOrNo

sync_hook.init_sync_hook()