import pytest

from passlib.context import CryptContext

from server.middleware.userauth import UserAuthentication

class TestPasswordHashing:
    DEFAULT_PASSWORD = 'password'
    # pre-generated hash using the same context in UserAuthentication
    DEFAULT_HASHED = '$pbkdf2-sha256$29000$6z0nxLh37v3fOydkjBHi3A$51waSF7m1N5sFyz/b9wfd6pcuWu4l0T1VceK3WcxJxI'

    def test_passwordHashingOfDefaultPasswordYieldsHashedString(self):
        hashed = UserAuthentication.hashPassword(self.DEFAULT_PASSWORD)
        
        assert hashed != None
        assert type(hashed) is str
        assert hashed != self.DEFAULT_PASSWORD
        assert hashed != self.DEFAULT_HASHED

    def test_passwordVerificationPassesAgainstDefaultPasswordAndDefaultHash(self):
        result = UserAuthentication.verifyPassword(self.DEFAULT_PASSWORD, self.DEFAULT_HASHED)

        assert result

    def test_passwordVeriicationPassesAgainstDefaultPasswordAndGeneratedHash(self):
        hashed = UserAuthentication.hashPassword(self.DEFAULT_PASSWORD)
        result = UserAuthentication.verifyPassword(self.DEFAULT_PASSWORD, hashed)

        assert result

    def test_passwordVerificationFailsAgainstWrongPasswordAndDefaultHash(self):
        password = 'wrong_password'
        hashed = UserAuthentication.hashPassword(password)
        result = UserAuthentication.verifyPassword(self.DEFAULT_PASSWORD, hashed)

        assert result == False

    def test_passwordVerificationFailsAgainstHashGeneratedByDifferentContext(self):
        difContextInfo = {
            'schemes': ['bcrypt'],
            'deprecated': 'auto',
        }
        difContext = CryptContext(**difContextInfo)
        hashed = difContext.hash(self.DEFAULT_PASSWORD)
        result = UserAuthentication.verifyPassword(self.DEFAULT_PASSWORD, hashed)

        assert result == False