import os
from selenium.webdriver import FirefoxProfile as BaseFirefoxProfile


class FirefoxProfile(BaseFirefoxProfile):

    def __init__(self, profile_directory=None):
        super(FirefoxProfile, self).__init__()

        if profile_directory:
            self.profile_dir = profile_directory
            self._read_existing_userjs(os.path.join(self.profile_dir, "user.js"))
            self.extensionsDir = os.path.join(self.profile_dir, "extensions")
            self.userPrefs = os.path.join(self.profile_dir, "user.js")
