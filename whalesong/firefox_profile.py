from os import path, remove, mkdir, makedirs
from selenium.webdriver import FirefoxProfile as BaseFirefoxProfile
from shutil import copyfile

TEMPLATE_DIR = path.join(path.dirname(__file__), 'firefox_profile_template')


class FirefoxProfile(BaseFirefoxProfile):

    def __init__(self, profile_directory=None):
        super(FirefoxProfile, self).__init__()

        if profile_directory:
            self.profile_dir = profile_directory

            makedirs(profile_directory, exist_ok=True)

            copyfile(path.join(TEMPLATE_DIR, 'addons.json'), path.join(self.profile_dir, 'addons.json'))
            copyfile(path.join(TEMPLATE_DIR, 'containers.json'), path.join(self.profile_dir, 'containers.json'))
            copyfile(path.join(TEMPLATE_DIR, 'extensions.json'), path.join(self.profile_dir, 'extensions.json'))
            copyfile(path.join(TEMPLATE_DIR, 'handlers.json'), path.join(self.profile_dir, 'handlers.json'))
            copyfile(path.join(TEMPLATE_DIR, 'prefs.js'), path.join(self.profile_dir, 'prefs.js'))
            copyfile(path.join(TEMPLATE_DIR, 'xulstore.json'), path.join(self.profile_dir, 'xulstore.json'))

            self.extensionsDir = path.join(self.profile_dir, "extensions")
            self.userPrefs = path.join(self.profile_dir, "user.js")
            try:
                remove(self.userPrefs)
            except FileNotFoundError:
                pass

            self.update_preferences()
