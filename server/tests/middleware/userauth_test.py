import pytest

from passlib.context import CryptContext

from server.middleware.userauth import UserAuthentication

class TestPasswordHashing:
    DEFAULT_PASSWORD = 'password'
    # pre-generated hash using the same context in UserAuthentication 'password'
    DEFAULT_HASHED = '$pbkdf2-sha256$29000$6z0nxLh37v3fOydkjBHi3A$51waSF7m1N5sFyz/b9wfd6pcuWu4l0T1VceK3WcxJxI'
    # pre-generated hash using different context and 'password'
    DIF_CONTEXT_HASHED = '$2b$12$m/c3kTn0DzeBAGAnUDqh3.yICIZAnQyqVB62aO6n9pLpW2uRsVVOa'

    def test_passwordHashingOfDefaultPasswordYieldsHashedString(self):
        hashed = UserAuthentication.hashPassword(self.DEFAULT_PASSWORD)
        
        assert hashed != None
        assert type(hashed) is str
        assert hashed != self.DEFAULT_PASSWORD
        assert hashed != self.DEFAULT_HASHED

    def test_passwordVerificationPassesAgainstDefaultPasswordAndDefaultHash(self):
        result = UserAuthentication.verifyPassword(self.DEFAULT_PASSWORD, self.DEFAULT_HASHED)

        assert result == True

    def test_passwordVeriicationPassesAgainstDefaultPasswordAndGeneratedHash(self):
        hashed = UserAuthentication.hashPassword(self.DEFAULT_PASSWORD)
        result = UserAuthentication.verifyPassword(self.DEFAULT_PASSWORD, hashed)

        assert result == True

    def test_passwordVerificationFailsAgainstWrongPasswordAndDefaultHash(self):
        password = 'wrong_password'
        result = UserAuthentication.verifyPassword(password, self.DEFAULT_HASHED)

        assert result == False

    def test_passwordVerificationFailsAgainstHashGeneratedByDifferentContext(self):
        result = UserAuthentication.verifyPassword(self.DEFAULT_PASSWORD, self.DIF_CONTEXT_HASHED)

        assert result == False