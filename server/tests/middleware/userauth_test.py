# -*- coding: utf-8 -*-
"""
This file houses tests for userauth.py
"""

from server.middleware.userauth import UserAuthentication


class TestPasswordHashing:
    DEFAULT_PASSWORD = 'password'
    # pre-generated hash for above password using the same context in UserAuthentication
    DEFAULT_HASHED = '$pbkdf2-sha256$29000$6z0nxLh37v3fOydkjBHi3A$51waSF7m1N5sFyz/b9wfd6pcuWu4l0T1VceK3WcxJxI'
    # pre-generated hash for above password using different context
    DIF_CONTEXT_HASHED = '$2b$12$m/c3kTn0DzeBAGAnUDqh3.yICIZAnQyqVB62aO6n9pLpW2uRsVVOa'

    def test_passwordHashingOfDefaultPasswordYieldsHashedString(self):
        hashed = UserAuthentication.hashPassword(self.DEFAULT_PASSWORD)
        
        assert hashed is not None
        assert type(hashed) is str
        assert hashed != self.DEFAULT_PASSWORD
        assert hashed != self.DEFAULT_HASHED

    def test_passwordVerificationPassesAgainstDefaultPasswordAndDefaultHash(self):
        assert UserAuthentication.verifyPassword(self.DEFAULT_PASSWORD, self.DEFAULT_HASHED)

    def test_passwordVeriicationPassesAgainstDefaultPasswordAndGeneratedHash(self):
        hashed = UserAuthentication.hashPassword(self.DEFAULT_PASSWORD)
        assert UserAuthentication.verifyPassword(self.DEFAULT_PASSWORD, hashed)

    def test_passwordVerificationFailsAgainstWrongPasswordAndDefaultHash(self):
        password = 'wrong_password'
        assert not UserAuthentication.verifyPassword(password, self.DEFAULT_HASHED)

    def test_passwordVerificationFailsAgainstHashGeneratedByDifferentContext(self):
        assert not UserAuthentication.verifyPassword(self.DEFAULT_PASSWORD, self.DIF_CONTEXT_HASHED)
