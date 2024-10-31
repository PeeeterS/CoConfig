import os, sys, json, base64, getpass
from typing import Any, Union


class BaseConfigManager:
    def __init__(self, config_filename: str = "config.json", defaultDict: dict = None) -> None:
        self.config_path = self._get_config_path(config_filename)
        self.defaultDict = defaultDict if defaultDict is not None else {}
        self.config = self._load_config()

    def _get_config_path(self, filename: str) -> str:
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, filename)
    
    def _load_config(self) -> Union[dict, list]:
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as file:
                return json.load(file)
        else:
            self._save_config(default=True)
            return self.defaultDict.copy()
    
    def _save_config(self, default: bool = False) -> bool:
        try:
            with open(self.config_path, "w") as file:                
                json.dump(self.config if not default else self.defaultDict, file, indent=4)
            return True
        except Exception as e:
            print(f"Config konnte nicht gespeichert werden.\n{e}")
            return False
    
    def remove(self, key: str) -> bool:
        print(f"Key: '{key}', Value: '{self.config.pop(key)}' has been removed")
        return self._save_config()


class GlobalConfigManager(BaseConfigManager):
    defaultDict = {
        "PRODUCTION_PATH": "/",
        "MACHINES": ["4.02", "4.03", "4.61", "4.62", "4.11", "5.25", "5.26", "5.27"],
        "SUBFOLDERS": ["Pressendaten", "SSG-PBS", "SSG-PBS-CSV", "TagesCSV"],
        "UPDATING": False,
        "LAST_UPDATE": ""
    }
    
    def __init__(self, config_path: str = "global_config.json") -> None:
        super().__init__(config_path, GlobalConfigManager.defaultDict)

    def get(self, key: str, default=None) -> Any:
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        self.config[key] = value        
        return self._save_config()


class UserConfigManager(BaseConfigManager):
    defaultAttributes = {
        "Favorites": [],
        "Theme": "normal",
        "Email": "",
        "Notifications": False
    }

    def __init__(self, config_path: str = "user_config.json") -> None:
        super().__init__(config_path)
        self._user = self._encode_item(getpass.getuser())  # Verwende den Windows-Benutzernamen als Key direkt
        if self._user not in self.config:
            self.config[self._user] = self.defaultAttributes.copy()
            self._save_config()

    def get(self, key: str, default=None) -> Any:
        user_data = self.config.get(self._user, {})
        if key == "Email" and user_data.get("Email"):
            return self._encode_item(user_data["Email"])
        return user_data.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        user_data = self.config.get(self._user, {})
        if key == "Email" and value:
            user_data[key] = self._encode_item(value)
        else:
            user_data[key] = value
        self.config[self._user] = user_data
        return self._save_config()

    def _encode_item(self, item: str) -> str:
        """Codiert die E-Mail in base64"""
        return base64.urlsafe_b64encode(item.encode()).decode()

    def _decode_item(self, item: str) -> str:
        """Decodiert die base64-codierte E-Mail"""
        return base64.urlsafe_b64decode(item.encode()).decode()
    

#class ConfigManager:
#    def create_manager(typ: str) -> BaseConfigManager:
#        if typ == "user_config.json":
#            return UserConfigManager(typ)
#        elif typ == "global_config.json":
#            return GlobalConfigManager(typ)
#        else:
#            raise ValueError("Unbekannter Konfigurationstyp. Verfügbar: 'user_config.json', 'global_config.json'.")