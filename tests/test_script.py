import unittest

from InstaLiveCLI import InstaLiveCLI

from .fixture import credentials


class TestAccountStandard(unittest.TestCase):
    def setUp(self):
        self.app = InstaLiveCLI(credentials.USERNAME,credentials.PASSWORD)

    def test_login(self):
        login = self.app.login()
        self.assertTrue(login)

class TestAccountTwoFactor(unittest.TestCase):
    def setUp(self):
        self.app = InstaLiveCLI(credentials.USERNAME_TWOFACTOR,credentials.PASSWORD_TWOFACTOR)

    def test_login_with_twofactor(self):
        login = self.app.login()

        if self.app.two_factor_required:
            two_factor = self.app.two_factor(code=input('Enter Code: '))
            self.assertTrue(two_factor)
