# -*- coding: utf-8 -*-
"""
This file houses tests for misc routes
"""


class TestMiscRoutes:
    def test_healthReturns200(self, client):
        response = client.get('/health')

        assert response.status_code == 200
        assert response.data == 'healthy'.encode('ascii')
