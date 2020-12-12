# -*- coding: utf-8 -*-
"""
This file houses tests for Post related routes available for this app
"""
import pytest

from server.config import Config
from server.entity import Post
from tests.helpers import create_mock_entities, create_testpost_attrs
import server.exceptions as exceptions

DEFAULT_RETURN_SEARCHPOST_ATTRSET = [
    create_testpost_attrs(postId='test_postid1'),
    create_testpost_attrs(postId='test_postid2'),
    create_testpost_attrs(postId='test_postid3'),
]
DEFAULT_RETURN_SEARCHPOST = create_mock_entities(DEFAULT_RETURN_SEARCHPOST_ATTRSET)
DEFAULT_RETURN_CREATENEWPOST = dict(created='post')
DEFAULT_RETURN_UPDATEPOST = 'some_value_updatepost'
DEFAULT_RETURN_DELETEPOST = dict(deleteCount=1)


@pytest.fixture(scope='function', autouse=True)
def set_mock_returnvalues(mockApp):
    Config.getCreationService(mockApp) \
        .createNewPost.return_value = DEFAULT_RETURN_CREATENEWPOST
    
    Config.getSearchService(mockApp) \
        .searchPostsByKeyValues.return_value = dict(posts=DEFAULT_RETURN_SEARCHPOST)

    Config.getUpdateService(mockApp) \
        .updatePost.return_value = DEFAULT_RETURN_UPDATEPOST

    Config.getDeleteService(mockApp) \
        .deletePostById.return_value = DEFAULT_RETURN_DELETEPOST


@pytest.fixture(scope='function', autouse=True)
def reset_mocks(mockApp):
    yield
    
    for mock in DEFAULT_RETURN_SEARCHPOST:
        mock.reset_mock(side_effect=True)

    Config.getCreationService(mockApp) \
        .createNewPost.reset_mock(side_effect=True)
    
    Config.getSearchService(mockApp) \
        .searchPostsByKeyValues.reset_mock(side_effect=True)

    Config.getUpdateService(mockApp) \
        .updatePost.reset_mock(side_effect=True)

    Config.getDeleteService(mockApp) \
        .deletePostById.reset_mock(side_effect=True)


class TestPostAPIs:
    POSTSAPI_BASE_URL = '/v1/posts'

    def test_searchPostsAPIPassesQueryStringToSearchService(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        keyValues = dict(
            search='1 2 3 4',
        )

        with mockApp.test_client() as client:
            client.get(self.POSTSAPI_BASE_URL, query_string=keyValues)

            mockSearch.searchPostsByKeyValues.assert_called_with(keyValues)

    def test_searchPostsAPICalls_to_serializeOnReturnedEntities(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        mock_posts = mockSearch.searchPostsByKeyValues.return_value['posts']
        keyValues = dict(
            search='1 2 3 4',
        )

        with mockApp.test_client() as client:
            client.get(self.POSTSAPI_BASE_URL, query_string=keyValues)

            for post in mock_posts:
                assert (post.to_serialize.call_count) == 1

    def test_searchPostsAPIReturns200AndWhatsReturnedFromService(self, mockApp):
        keyValues = dict(
            search='1 2 3 4',
        )

        with mockApp.test_client() as client:
            response = client.get(self.POSTSAPI_BASE_URL, query_string=keyValues)

            assert response.status_code == 200
            posts = response.get_json()['result']['posts']
            for post in posts:
                assert post in DEFAULT_RETURN_SEARCHPOST_ATTRSET

    def test_searchPostsReturnsErrorWhenExceptionWasRaised(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        exceptionsToTest = [
            exceptions.EntityValidationError,
            exceptions.FailedMongoOperation,
            exceptions.ServerMiscError
        ]
        keyValues = dict(
            search='1 2 3 4',
        )

        for e in exceptionsToTest:
            with mockApp.test_client() as client:
                mockSearch.searchPostsByKeyValues.side_effect = e()
                response = client.get(self.POSTSAPI_BASE_URL, query_string=keyValues)

                assert response.status_code == e.getStatusCode()

    def test_searchPostsAPIByIdPassesIdToSearchService(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        postId = '11223344'
        url = f'{self.POSTSAPI_BASE_URL}/{postId}'

        with mockApp.test_client() as client:
            client.get(url)

            mockSearch.searchPostsByKeyValues.assert_called_with(
                dict(postId=postId)
            )

    def test_searchPostsByIdAPIIgnoresQueryString(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        postId = '11223344'
        url = f'{self.POSTSAPI_BASE_URL}/{postId}'
        keyValues = dict(offset=30, limit=100)

        with mockApp.test_client() as client:
            client.get(url, query_string=keyValues)

            mockSearch.searchPostsByKeyValues.assert_called_with(dict(
                postId=postId
            ))

    def test_searchPostsByIdAPIReturns200AndWhatsReturnedFromService(self, mockApp):
        postId = '11223344'
        url = f'{self.POSTSAPI_BASE_URL}/{postId}'

        with mockApp.test_client() as client:
            response = client.get(url)

            print(response.get_json())
            assert response.status_code == 200
            posts = response.get_json()['result']['posts']
            for post in posts:
                assert post in DEFAULT_RETURN_SEARCHPOST_ATTRSET

    def test_searchPostsByIdAPIReturnsErrorWhenServiceRaisesException(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        exceptionsToTest = [
            exceptions.EntityValidationError,
            exceptions.FailedMongoOperation,
            exceptions.ServerMiscError
        ]
        postId = '11223344'
        url = f'{self.POSTSAPI_BASE_URL}/{postId}'

        for e in exceptionsToTest:
            with mockApp.test_client() as client:
                mockSearch.searchPostsByKeyValues.side_effect = e()
                response = client.get(url)

                assert response.status_code == e.getStatusCode()

    def test_createPostAPIPassesPostEntityToService(self, mockApp):
        mockCreate = Config.getCreationService(mockApp)
        newPostData = dict(
            content='This is a test post'
        )
        url = f'{self.POSTSAPI_BASE_URL}/create'

        with mockApp.test_client() as client:
            client.post(url, json=newPostData)

            post_passed, *_ = mockCreate.createNewPost.call_args_list[0][0]
            assert isinstance(post_passed, Post)
            for k, v in newPostData.items():
                assert getattr(post_passed, k) == v

    def test_createPostAPIReturns201AndReturnValueFromService(self, mockApp):
        Config.getCreationService(mockApp)
        newPostData = dict(
            content='This is a test post'
        )
        url = f'{self.POSTSAPI_BASE_URL}/create'

        with mockApp.test_client() as client:
            response = client.post(url, json=newPostData)

            assert response.status_code == 201
            assert response.get_json()['result'] == DEFAULT_RETURN_CREATENEWPOST

    def test_createPostAPIReturnsErrorWhenServiceRaisesException(self, mockApp):
        mockCreate = Config.getCreationService(mockApp)
        newPostData = dict(
            content='This is a test post'
        )
        url = f'{self.POSTSAPI_BASE_URL}/create'
        exceptionsToTest = [
            exceptions.EntityValidationError,
            exceptions.FailedMongoOperation,
            exceptions.ServerMiscError
        ]

        for e in exceptionsToTest:
            mockCreate.createNewPost.side_effect = e()
            with mockApp.test_client() as client:
                response = client.post(url, json=newPostData)

                assert response.status_code == e.getStatusCode()

    def test_updatePostShouldPassPostEntityToService(self, client, mockApp):
        mockUpdate = Config.getUpdateService(mockApp)
        postIdToUpdate = '1'
        url = f'{self.POSTSAPI_BASE_URL}/{postIdToUpdate}/update'
        updateData = {
            'content': 'Updated content!'
        }

        client.patch(url, json=updateData)

        assert mockUpdate.updatePost.call_count == 1
        post_passed, *_ = mockUpdate.updatePost.call_args_list[0][0]
        assert isinstance(post_passed, Post)
        for k, v in updateData.items():
            getattr(post_passed, k) == v
        assert getattr(post_passed, 'postId') == postIdToUpdate

    def test_updatePostShouldReturn200AndReturnValueFromService(self, client, mockApp):
        postIdToUpdate = '1'
        url = f'{self.POSTSAPI_BASE_URL}/{postIdToUpdate}/update'
        updateData = {
            'content': 'Updated content!'
        }

        response = client.patch(url, json=updateData)

        assert response.status_code == 200
        assert response.get_json()['result'] == DEFAULT_RETURN_UPDATEPOST

    def test_updatePostByPostedMimeTypeNotJsonReturnsError(self, client, mockApp):
        postIdToUpdate = '1'
        url = f'{self.POSTSAPI_BASE_URL}/{postIdToUpdate}/update'
        updateData = 'content'
        headers = { 'Content-Type': 'text/plain'}

        response = client.patch(url, data=updateData, headers=headers)

        assert response.status_code == 400

    def test_whenUpdatePostRaisesExceptionReturnError(self, mockApp):
        mockUpdate = Config.getUpdateService(mockApp)
        postIdToUpdate = '1'
        url = f'{self.POSTSAPI_BASE_URL}/{postIdToUpdate}/update'
        updateData = {
            'content': 'Updated content!'
        }
        exceptionsToTest = [
            exceptions.EntityValidationError('Some error'),
            exceptions.RecordNotFoundError('Some error'),
            exceptions.ServerMiscError('Some error'),
        ]

        for e in exceptionsToTest:
            mockUpdate.updatePost.side_effect = e
            with mockApp.test_client() as client:
                response = client.patch(url, json=updateData)

            assert response.status_code == e.getStatusCode()

    def test_deletePostByIdShouldPassPostIdToService(self, mockApp):
        postIdToDelete = '1'
        url = f'{self.POSTSAPI_BASE_URL}/{postIdToDelete}/delete'
        mockDelete = Config.getDeleteService(mockApp)

        with mockApp.test_client() as client:
            client.delete(url)

            mockDelete.deletePostById.assert_called_with(postIdToDelete)

    def test_deletePostByIdShouldReturn200AndResponseFromService(self, mockApp):
        postIdToDelete = '1'
        url = f'{self.POSTSAPI_BASE_URL}/{postIdToDelete}/delete'

        with mockApp.test_client() as client:
            response = client.delete(url)

            assert response.status_code == 200
            responseJson = response.get_json()
            responseJson['result'] == DEFAULT_RETURN_DELETEPOST

    def test_deletePostByIdShouldReturnsErrorWhenExceptionRaised(self, mockApp):
        postIdToDelete = '1'
        url = f'{self.POSTSAPI_BASE_URL}/{postIdToDelete}/delete'
        exceptionsToTest = [
            exceptions.RecordNotFoundError('Some error'),
            exceptions.ServerMiscError('Some error'),
        ]
        mockDelete = Config.getDeleteService(mockApp)

        for e in exceptionsToTest:
            mockDelete.deletePostById.side_effect = e
            with mockApp.test_client() as client:
                response = client.delete(url)

                assert response.status_code == e.getStatusCode()
