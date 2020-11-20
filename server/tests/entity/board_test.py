# -*- coding: utf-8 -*-
"""
This file houses tests for board.py
"""
import pytest

from server.entity import Board
from server.exceptions import EntityValidationError
from tests.helpers import create_mock_entities

DEFAULT_OWNER_ATTRS = [
    dict(userId='test_id')
]

DEFAULT_ARGS = {
    '_id': 'test_id',
    'boardId': 'test_board',
    'userId': 'test_user',
    'owner': create_mock_entities(DEFAULT_OWNER_ATTRS),
    'title': 'test_board_title',
    'createdAt': 123123.12,
    'updatedAt': 123123.12,
}


class TestBoardCreation:
    def test_construction_with_kwargs(self):
        board = Board(**DEFAULT_ARGS)

        assert board.boardId == DEFAULT_ARGS['boardId']
        for attr_name, attr_value in DEFAULT_ARGS.items():
            assert getattr(board, attr_name) == attr_value

    def test_construction_with_dict(self):
        board = Board(DEFAULT_ARGS)

        assert board.boardId == DEFAULT_ARGS['boardId']
        for attr_name, attr_value in DEFAULT_ARGS.items():
            assert getattr(board, attr_name) == attr_value

    def test_constructionIgnoresUnknownAttributes(self):
        unknown_attrs = {
            'hello': 'test_value',
            'foo': 'test_value',
            '123123': 'test_value',
            '!!!@#!@#': 'test_value',
        }

        board = Board({ **DEFAULT_ARGS, **unknown_attrs })

        for known_attr in DEFAULT_ARGS.keys():
            assert hasattr(board, known_attr)
        for unknown_attr in unknown_attrs.keys():
            assert not hasattr(board, unknown_attr)

    def test_constructionValidatesForType(self):
        wrongtype_attrs = dict(
            userId=9999,
            boardId=9999,
            owner=9999,
            title=9999,
            createdAt='11111111',
            updatedAt='11111111',
        )
        for wrong_attr, value in wrongtype_attrs.items():
            args = DEFAULT_ARGS.copy()
            args.update({ wrong_attr: value })

            with pytest.raises(EntityValidationError):
                Board(args)


class TestConversionMethods:
    @pytest.fixture(scope='function')
    def board(self):
        board = Board(DEFAULT_ARGS)

        for owner in board.owner:
            owner.reset_mock()

        return board

    def test_to_serialize(self, board):
        serialized = board.to_serialize()

        for attr, value in serialized.items():
            if attr == 'owner':
                assert DEFAULT_OWNER_ATTRS == value
            else:
                assert DEFAULT_ARGS[attr] == value

    def test_to_serializeCallsConvertDictForEachOwners(self, board):
        owners = board.owner

        try:
            board.to_serialize()
        except Exception:
            # ignore failed serialization during tests
            pass

        for owner in owners:
            assert owner._convert_dict_for.call_count == 1
            arg1, *_ = owner._convert_dict_for.call_args_list[0][0]
            assert arg1 == 'to_serialize'

    def test_to_serializeIgnoresUnnecessaryAttributes(self, board):
        private_attrs = ['_id', ]

        serialized = board.to_serialize()

        for attr in serialized.keys():
            assert attr not in private_attrs

    def test_to_serializeValidatesRequiredAttributes(self, board):
        required_attributes = [
            'boardId',
            'userId',
            'owner',
            'title',
            'createdAt',
        ]
        for required_attribute in required_attributes:
            args = DEFAULT_ARGS.copy()
            args.pop(required_attribute)
            board = Board(args)

            with pytest.raises(EntityValidationError):
                board.to_serialize()

    def test_to_serializeRaisesNoExceptionWhenMissingOptionalAttributes(self):
        optional_attributes = [
            'updatedAt',
        ]

        for optional_attribute in optional_attributes:
            args = DEFAULT_ARGS.copy()
            args.pop(optional_attribute)
            board = Board(args)

            board.to_serialize()

    def test_to_serializeContainsOptionalAttributes(self, board):
        optional_attributes = [
            'updatedAt',
        ]

        for optional_attribute in optional_attributes:
            assert hasattr(board, optional_attribute)

    def test_to_createGeneratesDictForCreation(self, board):
        create_dict = board.to_create()

        for attr, value in create_dict.items():
            assert DEFAULT_ARGS[attr] == value

    def test_to_createValidatesForRequiredAttributes(self):
        required_attributes = [
            'boardId',
            'userId',
            'title',
            'createdAt',
        ]
        for required_attribute in required_attributes:
            args = DEFAULT_ARGS.copy()
            args.pop(required_attribute)
            board = Board(args)

            with pytest.raises(EntityValidationError):
                board.to_create()

    def test_to_createIgnoresUnnecessaryAttributes(self, board):
        ignored_args = [
            '_id',
            'owner',
            'updatedAt',
        ]

        create_dict = board.to_create()
        
        for attr in ignored_args:
            assert attr not in create_dict

    def test_to_updateGeneratesDictForUpdate(self, board):
        update_dict = board.to_update()

        for attr, value in update_dict.items():
            assert DEFAULT_ARGS[attr] == value

    def test_to_updateIgnoresUnnecessaryAttributes(self, board):
        ignored_args = [
            '_id',
            'boardId',
            'userId',
            'owner',
            'createdAt',
        ]

        update_dict = board.to_update()

        for ignored_attr in ignored_args:
            assert ignored_attr not in update_dict

    def test_to_updateGeneratesDictWithOptionalAttributes(self, board):
        optional_attrs = [
            'title',
        ]

        update_dict = board.to_update()

        for optional_attr in optional_attrs:
            assert optional_attr in update_dict
            assert DEFAULT_ARGS[optional_attr] == update_dict[optional_attr]


class TestSearch:
    pass
