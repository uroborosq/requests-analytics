import json
import pickle


class AutocompletionUnit:
    comp: dict[str, object]

    def __init__(self, save_func):
        self.comp = {}
        self.__save_func__ = save_func

    def get(self, key: str):
        return self.comp.get(key)

    def set(self, key: str, value) -> None:
        self.comp[key] = value
        self.__save_func__()


class Settings:
    version: str
    autocompletion: dict[str, AutocompletionUnit]
    priorities: list[str]
    columns: dict[str, str]

    def __init__(self):
        self.version = "2.0.0 alpha"
        self.priorities = []
        self.columns = {}
        self.autocompletion = {}

    def set_default(self):
        self.version = "2.0.0 alpha"
        self.priorities = ['Гарантия14 дн.', 'ФОК-Гарантия', 'Население-Гарантия', 'ФОК-Платно', 'Население-платно', 'Внутренние работы']
        self.columns = {}
        self.autocompletion = {}


class SettingsManager:
    __file_settings_path__: str
    __settings__: Settings

    def __init__(self, file_settings_path: str):
        try:
            self.__file_settings_path__ = file_settings_path
            settings_file = open(self.__file_settings_path__, 'rb')
            self.__settings__ = pickle.load(settings_file, fix_imports=True)
            settings_file.close()
        except Exception as e:
            self.set_default()

    def get_autocompletion(self, autocompletion_unit: str, key: str) -> str | None:
        unit = self.__settings__.autocompletion.get(autocompletion_unit)
        if unit is None:
            return None
        return unit.get(key)

    def set_autocompletion(self, autocompletion_unit: str, key: str, value: str) -> None:
        if self.__settings__.autocompletion.get(autocompletion_unit) is None:
            self.__settings__.autocompletion[autocompletion_unit] = AutocompletionUnit(self.save)
        self.__settings__.autocompletion[autocompletion_unit].set(key, value)
        self.save()

    def set_default(self):
        self.__settings__ = Settings()
        self.__settings__.set_default()
        self.save()

    def get_version(self) -> str:
        return self.__settings__.version

    def get_priorities(self) -> list[str]:
        return self.__settings__.priorities

    def set_priorities(self, new_priorities: list[str]) -> None:
        self.__settings__.priorities = new_priorities
        self.save()

    def get_autocompletion_unit(self, key):
        unit = self.__settings__.autocompletion.get(key)
        if unit is None:
            self.__settings__.autocompletion[key] = AutocompletionUnit(self.save)
        return self.__settings__.autocompletion[key]

    def save(self):
        settings_file = open(self.__file_settings_path__, 'wb')
        pickle.dump(self.__settings__, settings_file, fix_imports=True)
        settings_file.close()

