# -*- coding: utf-8 -*-
"""
This file houses tests for Thread entity
"""

import pytest

from server.entity import Thread
from server.exceptions import EntityValidationError
from tests.helpers import create_mock_entities

DEFAULT_OWNER_ATTRS = [
    dict(userId='test_userid'),
]

DEFAULT_LASTPOST_ATTRS = [
    dict(postId='test_postid'),
]

DEFAULT_ARGS = {
    'userId': 'test_thread',
    'boardId': 'test_id',
    'threadId': 'test_id',
    'lastPostId': 'test_id',
    'owner': create_mock_entities(DEFAULT_OWNER_ATTRS),
    'lastPost': create_mock_entities(DEFAULT_LASTPOST_ATTRS),
    'title': 'Anonymous\'s thread',
    'subject': 'test_subject',
    'increment': 'views',
    'views': 0,
    'postCount': 0,
    'createdAt': 123123.12,
    'updatedAt': 123123.12,
}


class TestThreadCreation:
    def test_construction_with_kwargs(self):
        thread = Thread(**DEFAULT_ARGS)

        assert thread.threadId == DEFAULT_ARGS['threadId']
        for attr_name, attr_value in DEFAULT_ARGS.items():
            assert getattr(thread, attr_name) == attr_value

    def test_construction_with_dict(self):
        thread = Thread(DEFAULT_ARGS)

        assert thread.threadId == DEFAULT_ARGS['threadId']
        for attr_name, attr_value in DEFAULT_ARGS.items():
            assert getattr(thread, attr_name) == attr_value

    def test_constructionIgnoresUnknownAttributes(self):
        unknown_attrs = {
            'hello': 'test_value',
            'foo': 'test_value',
            '123123': 'test_value',
            '!!!@#!@#': 'test_value',
        }

        thread = Thread({ **DEFAULT_ARGS, **unknown_attrs })

        for known_attr in DEFAULT_ARGS.keys():
            assert hasattr(thread, known_attr)
        for unknown_attr in unknown_attrs.keys():
            assert not hasattr(thread, unknown_attr)

    def test_constructionValidatesForType(self):
        wrongtype_attrs = dict(
            userId=9999,
            boardId=9999,
            threadId=9999,
            lastPostId=9999,
            owner=9999,
            lastPost=9999,
            title=9999,
            subject=9999,
            views='test_value',
            postCount='test_value',
            increment=9999,
            createdAt='123123.12',
            updatedAt='123123.12',
        )
        for wrong_attr, value in wrongtype_attrs.items():
            args = DEFAULT_ARGS.copy()
            args.update({ wrong_attr: value })

            with pytest.raises(EntityValidationError):
                Thread(args)

    def test_constructionValidatesTitleIsNotEmptyOrSpaces(self):
        wrong_strings = [
            '',
            ' ',
            '\t\t ',
        ]
        for wrong_string in wrong_strings:
            args = DEFAULT_ARGS.copy()
            args.update({ 'title': wrong_string })

            with pytest.raises(EntityValidationError):
                Thread(args)

    def test_constructionValidatesSubjectIsNotEmptyOrSpaces(self):
        wrong_strings = [
            '',
            ' ',
            '\t\t ',
        ]
        for wrong_string in wrong_strings:
            args = DEFAULT_ARGS.copy()
            args.update({ 'subject': wrong_string })

            with pytest.raises(EntityValidationError):
                Thread(args)

    def test_constructionValidatesIncrementString(self):
        wrong_strings = [
            'view',
            'title',
            'subject',
            '11233123',
            '!@#!@#!23',
        ]
        for wrong_string in wrong_strings:
            args = DEFAULT_ARGS.copy()
            args.update({ 'increment': wrong_string })
            
            with pytest.raises(EntityValidationError):
                Thread(args)

    def test_constructionAllowsNoneLastPostId(self):
        attr = { 'lastPostId': None }
        
        thread = Thread({ **DEFAULT_ARGS, **attr })

        assert getattr(thread, 'lastPostId') is None


class TestConversionMethods:
    @pytest.fixture(scope='function')
    def thread(self):
        thread = Thread(DEFAULT_ARGS)

        for owner in thread.owner:
            owner.reset_mock()
        for lastpost in thread.lastPost:
            lastpost.reset_mock()

        return thread

    def test_to_serialize(self, thread):
        serialized = thread.to_serialize()

        for attr, value in serialized.items():
            if attr == 'owner':
                assert DEFAULT_OWNER_ATTRS == value
            elif attr == 'lastPost':
                assert DEFAULT_LASTPOST_ATTRS == value
            else:
                assert DEFAULT_ARGS[attr] == value

    def test_to_serializeCallsConvertDictForEachOwners(self, thread):
        owners = thread.owner

        try:
            thread.to_serialize()
        except Exception:
            # ignore failed serialization during tests
            pass

        for owner in owners:
            assert owner._convert_dict_for.call_count == 1
            arg1, *_ = owner._convert_dict_for.call_args_list[0][0]
            assert arg1 == 'to_serialize'

    def test_to_serializeCallsConvertDictForEachLastPost(self, thread):
        lastpost = thread.lastPost[0]

        try:
            thread.to_serialize()
        except Exception:
            # ignore failed serialization during tests
            pass

        assert lastpost._convert_dict_for.call_count == 1
        arg1, *_ = lastpost._convert_dict_for.call_args_list[0][0]
        assert arg1 == 'to_serialize'

    def test_to_serializeIgnoresUnnecessaryAttributes(self, thread):
        private_attrs = ['_id', 'increment', ]

        serialized = thread.to_serialize()

        for attr in serialized.keys():
            assert attr not in private_attrs

    def test_to_serializeValidatesRequiredAttributes(self, thread):
        required_attributes = [
            'threadId',
            'boardId',
            'owner',
            'lastPost',
            'title',
            'subject',
            'views',
            'postCount',
            'createdAt',
        ]
        for required_attribute in required_attributes:
            args = DEFAULT_ARGS.copy()
            args.pop(required_attribute)
            thread = Thread(args)

            with pytest.raises(EntityValidationError):
                thread.to_serialize()

    def test_to_serializeRaisesNoExceptionWhenMissingOptionalAttributes(self):
        optional_attributes = [
            'updatedAt',
        ]

        for optional_attribute in optional_attributes:
            args = DEFAULT_ARGS.copy()
            args.pop(optional_attribute)
            thread = Thread(args)

            thread.to_serialize()

    def test_to_serializeContainsOptionalAttributes(self, thread):
        optional_attributes = [
            'updatedAt',
        ]

        for optional_attribute in optional_attributes:
            assert hasattr(thread, optional_attribute)

    def test_to_createGeneratesDictForCreation(self, thread):
        create_dict = thread.to_create()

        for attr, value in create_dict.items():
            assert DEFAULT_ARGS[attr] == value

    def test_to_createValidatesForRequiredAttributes(self):
        required_attributes = [
            'userId',
            'boardId',
            'lastPostId',
            'title',
            'subject',
            'views',
            'postCount',
        ]
        for required_attribute in required_attributes:
            args = DEFAULT_ARGS.copy()
            args.pop(required_attribute)
            thread = Thread(args)

            with pytest.raises(EntityValidationError):
                thread.to_create()

    def test_to_createIgnoresUnnecessaryAttributes(self, thread):
        ignored_args = [
            'threadId',
            '_id',
            'increment',
            'owner',
            'lastPost',
            'createdAt',
            'updatedAt',
        ]

        create_dict = thread.to_create()
        
        for attr in ignored_args:
            assert attr not in create_dict

    def test_to_updateGeneratesDictForUpdate(self, thread):
        update_dict = thread.to_update()

        for attr, value in update_dict.items():
            assert DEFAULT_ARGS[attr] == value

    def test_to_updateIgnoresUnnecessaryAttributes(self, thread):
        ignored_args = [
            '_id',
            'threadId',
            'userId',
            'boardId',
            'owner',
            'lastPost',
            'createdAt',
            'updatedAt',
        ]

        update_dict = thread.to_update()

        for ignored_attr in ignored_args:
            assert ignored_attr not in update_dict

    def test_to_updateGeneratesDictWithOptionalAttributes(self, thread):
        optional_attrs = [
            'title',
            'subject',
            'lastPostId',
            'views',
            'postCount',
            'increment',
        ]

        update_dict = thread.to_update()

        for optional_attr in optional_attrs:
            assert optional_attr in update_dict
            assert DEFAULT_ARGS[optional_attr] == update_dict[optional_attr]


class TestSearch:
    def test_someattrs_are_fuzzysearchable(self):
        fuzzy_searchables = ['title', 'subject']

        for attr in fuzzy_searchables:
            search_rules = Thread._attribute_description[attr]['search_rules']
            assert search_rules['fuzzy'] is True
