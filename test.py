from config_manager import UserConfigManager
from config_manager import GlobalConfigManager

meinManager = GlobalConfigManager()
userManager = UserConfigManager()

userManager.set("Email", "a")
