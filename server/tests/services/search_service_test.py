# -*- coding: utf-8 -*-
"""
This file houses test code for search_service.py
"""
import pytest
from unittest.mock import ANY

from server.database.sorter import AscendingSorter, DescendingSorter, NullSorter
from server.services.search_service import SearchService
from server.database.filter import PrimitiveFilter
from server.database.aggregate_filter import AggregateFilter
import tests.mocks as mocks
from tests.mocks import createMockEntity
from tests.helpers import create_mock_entities


@pytest.fixture(scope='function')
def service():
    mockRepo = mocks.createMockRepo()
    mockSearchCreator = mocks.createMockSearchFilterCreatorService()
    mockPaging = mocks.createMockPaging()

    yield SearchService(mockRepo, mockSearchCreator, PrimitiveFilter, AggregateFilter, mockPaging)


class TestSearchUsersByKeyValues:
    MOCKDB_DEFAULT_RETURN = dict(
        users=[ createMockEntity(), createMockEntity() ],
        returnCount=2,
        matchedCount=2,
    )
    MOCKPAGING_DEFAULT_RETURN = 'default_paging'
    DEFAULT_KEYVALUES = dict(
        search='username1',
        userId='11223344',
    )
    MOCK_SEARCHFILTER = 'some_mock_value'

    @pytest.fixture(scope='function', autouse=True)
    def setDefaultReturnValues(self, service):
        service._repo.searchUser.return_value = self.MOCKDB_DEFAULT_RETURN
        service._paging.return_value = self.MOCKPAGING_DEFAULT_RETURN
        service._searchFilterCreator.create_usersearch.return_value = self.MOCK_SEARCHFILTER

    def test_searchUsersByKeyValuesPassesKeyValuesToSearchFilterCreator(self, service):
        creator = service._searchFilterCreator

        service.searchUsersByKeyValues(self.DEFAULT_KEYVALUES)

        assert len(creator.create_usersearch.call_args_list) > 0
        passed_arg, *_ = creator.create_usersearch.call_args_list[0][0]
        assert passed_arg == self.DEFAULT_KEYVALUES

    def test_searchUsersByKeyValuesPassesSearchFilterToRepo(self, service):
        repo = service._repo

        service.searchUsersByKeyValues(self.DEFAULT_KEYVALUES)

        assert len(repo.searchUser.call_args_list) > 0
        passed_filter, *_ = repo.searchUser.call_args_list[0][0]
        assert passed_filter == self.MOCK_SEARCHFILTER

    def test_searchUserByKeyValuesPassesKeyValuessToPaging(self, service):
        mockPaging = service._paging
        
        service.searchUsersByKeyValues(self.DEFAULT_KEYVALUES)

        mockPaging.assert_called_with(self.DEFAULT_KEYVALUES)

    def test_searchUsersByKeyValuesQueriesCrudWithCreatedPagingAndFilter(self, service):
        mockRepo = service._repo

        service.searchUsersByKeyValues(self.DEFAULT_KEYVALUES)

        mockRepo.searchUser.assert_called_with(
            ANY,
            paging=self.MOCKPAGING_DEFAULT_RETURN, sorter=NullSorter()
        )

    def test_searchUserByKeyValuesShouldPassAscSorterToRepoWhenSpecifiedSortBy(self, service):
        mockRepo = service._repo
        keyValues = self.DEFAULT_KEYVALUES.copy()
        keyValues['sortBy'] = 'some_field'
        expectedSorter = AscendingSorter('some_field')

        service.searchUsersByKeyValues(keyValues)

        mockRepo.searchUser.assert_called_with(
            ANY, paging=ANY, sorter=expectedSorter
        )

    def test_searchUserByKeyValuesShouldPassDescSorterToRepoWhenSpecifiedSortByAndDescOrder(self, service):
        mockRepo = service._repo
        keyValues = self.DEFAULT_KEYVALUES.copy()
        keyValues['sortBy'] = 'some_field'
        keyValues['order'] = 'desc'
        expectedSorter = DescendingSorter('some_field')

        service.searchUsersByKeyValues(keyValues)

        mockRepo.searchUser.assert_called_with(
            ANY, paging=ANY, sorter=expectedSorter
        )

    def test_searchUsersByKeyValuesReturnFilteredReturnUsersFromQuery(self, service):
        searchResult = service.searchUsersByKeyValues(self.DEFAULT_KEYVALUES)

        assert searchResult == self.MOCKDB_DEFAULT_RETURN


class TestSearchPostsByKeyValues:
    DEFAULT_POST_OWNERID = 'test_id'
    DEFAULT_KEYVALUES = dict(search='some_content', postId='test_postid')
    MOCK_POST_ATTRSET = [
        dict(postId='test_postid', userId='test_userid')
    ]
    MOCK_USER_ATTRSET = [
        dict(userId='test_userid'),
        dict(userId='test_userid1'),
        dict(userId='test_userid2'),
    ]
    MOCK_SEARCHFILTER = 'test_search_filter'
    MOCKPAGING_DEFAULT_RETURN = 'default_paging'

    @pytest.fixture(scope='function', autouse=True)
    def setDefaultReturnValues(self, service):
        mock_posts = create_mock_entities(self.MOCK_POST_ATTRSET)
        mock_users = create_mock_entities(self.MOCK_USER_ATTRSET)
        searchpost_return = create_return_from_repo(mock_posts, 'posts')
        searchuser_return = create_return_from_repo(mock_users, 'users')

        service._repo.searchPost.return_value = searchpost_return
        service._repo.searchUser.return_value = searchuser_return
        service._searchFilterCreator.create_postsearch.return_value = self.MOCK_SEARCHFILTER
        service._paging.return_value = self.MOCKPAGING_DEFAULT_RETURN

    def test_searchPostsByKeyValuesPassesKeyValuesToSearchFilterCreator(self, service):
        creator = service._searchFilterCreator

        service.searchPostsByKeyValues(self.DEFAULT_KEYVALUES)

        assert len(creator.create_postsearch.call_args_list) > 0
        passed_arg, *_ = creator.create_postsearch.call_args_list[0][0]
        assert passed_arg == self.DEFAULT_KEYVALUES

    def test_searchPostsByKeyValuesPassesSearchFilterToRepo(self, service):
        repo = service._repo

        service.searchPostsByKeyValues(self.DEFAULT_KEYVALUES)

        assert len(repo.searchPost.call_args_list) > 0
        passed_filter, *_ = repo.searchPost.call_args_list[0][0]
        assert passed_filter == self.MOCK_SEARCHFILTER

    def test_searchPostsByKeyValuesPassesDefaultPagingToQuery(self, service):
        mockRepo = service._repo

        service.searchPostsByKeyValues(self.DEFAULT_KEYVALUES)

        mockRepo.searchPost.assert_any_call(
            ANY,
            paging=self.MOCKPAGING_DEFAULT_RETURN,
            sorter=NullSorter()
        )

    def test_searchPostsByKeyValuesPassesAscSorterToQueryWhenSortInKeyValues(self, service):
        mockRepo = service._repo
        keyValues = self.DEFAULT_KEYVALUES.copy()
        keyValues['sortBy'] = 'createdAt'
        expectedSorter = AscendingSorter('createdAt')

        service.searchPostsByKeyValues(keyValues)

        mockRepo.searchPost.assert_any_call(
            ANY,
            paging=ANY,
            sorter=expectedSorter,
        )

    def test_searchPostsByKeyValuessDescSorterToQueryWhenDescOrderWasSpecified(self, service):
        mockRepo = service._repo
        keyValues = self.DEFAULT_KEYVALUES.copy()
        keyValues['sortBy'] = 'createdAt'
        keyValues['order'] = 'desc'
        expectedSorter = DescendingSorter('createdAt')

        service.searchPostsByKeyValues(keyValues)

        mockRepo.searchPost.assert_any_call(
            ANY,
            paging=ANY,
            sorter=expectedSorter
        )

    def test_searchPostsByKeyValuesSearchesForOwnerId(self, service):
        repo = service._repo
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='userId',
            operator='eq',
            value=[ self.MOCK_POST_ATTRSET[0]['userId'] ]
        ))

        service.searchPostsByKeyValues(self.DEFAULT_KEYVALUES)

        narrowing_filter = repo.searchUser.call_args_list[0][0][0]
        assert narrowing_filter == expected_filter

    def test_searchPostsByKeyValuesSearchesOwnerUsersForMultiplePosts(self, service):
        repo = service._repo
        mock_attrset = [
            dict(postId='test_postid1', userId='test_userid_1'),
            dict(postId='test_postid2', userId='test_userid_2'),
            dict(postId='test_postid3', userId='test_userid_3'),
        ]
        owner_ids = [ attr['userId'] for attr in mock_attrset ]
        mock_posts = create_mock_entities(mock_attrset)
        repo.searchPost.return_value = create_return_from_repo(mock_posts, 'posts')
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='userId',
            operator='eq',
            value=owner_ids
        ))

        service.searchPostsByKeyValues(self.DEFAULT_KEYVALUES)

        narrowing_filter = repo.searchUser.call_args_list[0][0][0]
        assert narrowing_filter == expected_filter

    def test_searchPostsByKeyValuesShouldNotSearchForOwnerWhenNoPostReturned(self, service):
        repo = service._repo
        repo.searchPost.return_value = create_return_from_repo([], 'posts')

        service.searchPostsByKeyValues(self.DEFAULT_KEYVALUES)

        assert repo.searchUser.call_count == 0

    def test_searchPostsByKeyValuesReturnPosts(self, service):
        expected_post = self.MOCK_POST_ATTRSET[0]

        searchResult = service.searchPostsByKeyValues(self.DEFAULT_KEYVALUES)

        assert len(searchResult['posts']) == len(self.MOCK_POST_ATTRSET)
        assert searchResult['returnCount'] == len(self.MOCK_POST_ATTRSET)
        assert searchResult['matchedCount'] == len(self.MOCK_POST_ATTRSET)
        post = searchResult['posts'][0]
        for k, v in expected_post.items():
            assert getattr(post, k) == v
        
    def test_searchPostsByKeyValuesReturnPostsWithOwnerId(self, service):
        expected_owner = self.MOCK_USER_ATTRSET[0]

        searchResult = service.searchPostsByKeyValues(self.DEFAULT_KEYVALUES)
        
        post = searchResult['posts'][0]
        owner = getattr(post, 'owner')
        assert len(owner) == 1
        for k, v in expected_owner.items():
            assert getattr(owner[0], k) == v


class TestSearchThreadsByKeyValues:
    DEFAULT_KEYVALUES = dict(
        userId='test_id',
        search='test_search',
    )
    MOCK_THREAD_ATTRSET = [
        dict(threadId='2222', userId='11111111', boardid='123123', _id='some_random_id', lastPostId='1234')
    ]
    MOCK_USER_ATTRSET = [
        dict(userId='11111111', name='Alan', _id='some_random_id'),
        dict(userId='33333333', name='Bobby', _id='some_random_id'),
    ]
    MOCK_BOARD_ATTRSET = [
        dict(boardId='123123'),
        dict(boardId='234234'),
    ]
    MOCK_POST_ATTRSET = [
        dict(postId='1234', userId='33333333'),
        dict(postId='3456', userId='33333333'),
        dict(postId='4567', userId='33333333'),
    ]
    MOCK_SEARCHFILTER = 'test_search_filter'
    MOCKPAGING_DEFAULT_RETURN = 'default_paging'

    @pytest.fixture(scope='function', autouse=True)
    def setDefaultReturnValues(self, service):
        mock_threads = create_mock_entities(self.MOCK_THREAD_ATTRSET)
        threads_from_repo = create_return_from_repo(mock_threads, 'threads')
        mock_users = create_mock_entities(self.MOCK_USER_ATTRSET)
        users_from_repo = create_return_from_repo(mock_users, 'users')
        mock_boards = create_mock_entities(self.MOCK_BOARD_ATTRSET)
        boards_from_repo = create_return_from_repo(mock_boards, 'boards')
        mock_posts = create_mock_entities(self.MOCK_POST_ATTRSET)
        posts_from_repo = create_return_from_repo(mock_posts, 'posts')

        service._repo.searchThread.return_value = threads_from_repo
        service._repo.searchUser.return_value = users_from_repo
        service._repo.searchPost.return_value = posts_from_repo
        service._searchFilterCreator.create_threadsearch.return_value = self.MOCK_SEARCHFILTER
        service._paging.return_value = self.MOCKPAGING_DEFAULT_RETURN

    def test_searchThreadsByKeyValuesPassesKeyValuesToSearchFilterCreator(self, service):
        creator = service._searchFilterCreator

        service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)

        assert len(creator.create_threadsearch.call_args_list) > 0
        passed_arg, *_ = creator.create_threadsearch.call_args_list[0][0]
        assert passed_arg == self.DEFAULT_KEYVALUES

    def test_searchThreadsByKeyValuesPassesSearchFilterToRepo(self, service):
        repo = service._repo

        service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)

        assert len(repo.searchThread.call_args_list) > 0
        passed_filter, *_ = repo.searchThread.call_args_list[0][0]
        assert passed_filter == self.MOCK_SEARCHFILTER

    def test_searchThreadsByKeyValuesShouldPassKeyValuesToPaging(self, service):
        mockPaging = service._paging

        service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)

        mockPaging.assert_called_with(self.DEFAULT_KEYVALUES)

    def test_searchThreadByKeyValuesPassesAscSorterToQueryWhenSortInKeyValues(self, service):
        mockRepo = service._repo
        keyValues = self.DEFAULT_KEYVALUES.copy()
        keyValues['sortBy'] = 'createdAt'
        expectedSorter = AscendingSorter('createdAt')

        service.searchThreadsByKeyValues(keyValues)

        mockRepo.searchThread.assert_any_call(
            ANY,
            paging=ANY,
            sorter=expectedSorter,
        )

    def test_searchThreadByKeyValuessDescSorterToQueryWhenDescOrderWasSpecified(self, service):
        mockRepo = service._repo
        keyValues = self.DEFAULT_KEYVALUES.copy()
        keyValues['sortBy'] = 'createdAt'
        keyValues['order'] = 'desc'
        expectedSorter = DescendingSorter('createdAt')

        service.searchThreadsByKeyValues(keyValues)

        mockRepo.searchThread.assert_any_call(
            ANY,
            paging=ANY,
            sorter=expectedSorter
        )

    def test_searchThreadsByKeyValuesShouldNotUpdateThreadViewCount(self, service):
        mockRepo = service._repo

        service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)

        assert mockRepo.updateThread.call_count == 0

    def test_searchThreadsByKeyValuesShouldGenerateSearchForOwnerUser(self, service):
        mockRepo = service._repo
        owner_ids = [ attrs['userId'] for attrs in self.MOCK_THREAD_ATTRSET ]
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='userId',
            operator='eq',
            value=owner_ids
        ))

        service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)

        passed_filter, *_ = mockRepo.searchUser.call_args_list[0][0]
        assert passed_filter == expected_filter

    def test_searchThreadsByKeyValuesShouldGenerateSearchForAllOwners(self, service):
        repo = service._repo
        thread_attrs = [
            dict(threadId='test_1', userId='user_1', lastPostId='post_1'),
            dict(threadId='test_2', userId='user_2', lastPostId='post_2'),
            dict(threadId='test_3', userId='user_3', lastPostId='post_3'),
        ]
        mock_threads = create_mock_entities(thread_attrs)
        repo.searchThread.return_value = create_return_from_repo(mock_threads, 'threads')
        owner_ids = [ attrs['userId'] for attrs in thread_attrs ]
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='userId',
            operator='eq',
            value=owner_ids
        ))

        service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)

        passed_filter, *_ = repo.searchUser.call_args_list[0][0]
        assert passed_filter == expected_filter

    def test_searchThreadsByKeyValuesShouldGenerateSearchForLastPost(self, service):
        repo = service._repo
        lastpost_ids = [ attrs['lastPostId'] for attrs in self.MOCK_THREAD_ATTRSET ]
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='postId',
            operator='eq',
            value=lastpost_ids
        ))

        service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)

        passed_filter, *_ = repo.searchPost.call_args_list[0][0]
        assert passed_filter == expected_filter

    def test_searchThreadsByKeyValuesShouldGenerateSearchForAllLastPosts(self, service):
        repo = service._repo
        thread_attrs = [
            dict(threadId='test_1', userId='user_1', lastPostId='post_1'),
            dict(threadId='test_2', userId='user_2', lastPostId='post_2'),
            dict(threadId='test_3', userId='user_3', lastPostId='post_3'),
        ]
        mock_threads = create_mock_entities(thread_attrs)
        repo.searchThread.return_value = create_return_from_repo(mock_threads, 'threads')
        lastpost_ids = [ attrs['lastPostId'] for attrs in thread_attrs ]
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='postId',
            operator='eq',
            value=lastpost_ids
        ))

        service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)

        passed_filter, *_ = repo.searchPost.call_args_list[0][0]
        assert passed_filter == expected_filter

    def test_searchThreadsByKeyValuesShouldIgnoreEmptyLastPostId(self, service):
        repo = service._repo
        thread_attrs = [
            dict(threadId='test_1', userId='user_1', lastPostId=None),
            dict(threadId='test_2', userId='user_2', lastPostId=None),
            dict(threadId='test_3', userId='user_3', lastPostId='post_3'),
        ]
        mock_threads = create_mock_entities(thread_attrs)
        repo.searchThread.return_value = create_return_from_repo(mock_threads, 'threads')
        lastpost_ids = [
            attrs['lastPostId']
            for attrs in thread_attrs
            if attrs['lastPostId'] is not None
        ]
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='postId',
            operator='eq',
            value=lastpost_ids
        ))

        service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)

        passed_filter, *_ = repo.searchPost.call_args_list[0][0]
        assert passed_filter == expected_filter

    def test_searchThreadsByKeyValuesShouldNotSearchForLastPostOrOwnerWhenNoThreadReturned(self, service):
        repo = service._repo
        repo.searchThread.return_value = create_return_from_repo([], 'threads')

        service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)

        assert repo.searchUser.call_count == 0
        assert repo.searchPost.call_count == 0

    def test_searchThreadsByKeyValuesShouldReturnSearchResult(self, service):
        result = service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)

        threads = result['threads']
        assert len(threads) == len(self.MOCK_THREAD_ATTRSET)
        assert result['returnCount'] == len(threads)
        assert result['matchedCount'] == len(threads)
        for k, v in self.MOCK_THREAD_ATTRSET[0].items():
            assert getattr(threads[0], k) == v

    def test_searchThreadsByKeyValuesReturnThreadsWithOwnerUser(self, service):
        result = service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)

        threads = result['threads']
        for thread in threads:
            owner = getattr(thread, 'owner')
            assert len(owner) == 1
            assert getattr(owner[0], 'userId') == getattr(thread, 'userId')

    def test_searchThreadsByKeyValuesShouldContainLastPostInfo(self, service):
        result = service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)
        expected_lastpost_attrs = self.MOCK_POST_ATTRSET[0]

        thread = result['threads'][0]
        lastposts = getattr(thread, 'lastPost')
        assert len(lastposts) == 1
        for k, v in expected_lastpost_attrs.items():
            assert getattr(lastposts[0], k) == v

    def test_searchThreadsByKeyValuesShouldHaveEmptyLastpostsWhenNoMatchingPostFound(self, service):
        repo = service._repo
        thread_attrset = [
            dict(threadId='test_id1', userId='test_user1', lastPostId='nonexistant_id'),
            dict(threadId='test_id2', userId='test_user1', lastPostId='nonexistant_id'),
            dict(threadId='test_id3', userId='test_user1', lastPostId='nonexistant_id'),
        ]
        mock_threads = create_mock_entities(thread_attrset)
        repo.searchThread.return_value = create_return_from_repo(mock_threads, 'threads')

        result = service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)

        for thread in result['threads']:
            lastposts = getattr(thread, 'lastPost')
            assert len(lastposts) == 0
            

class TestSearchThreadByExplicitId:
    DEFAULT_THREAD_ID = 'test_id'
    MOCK_THREAD_ATTRSET = [
        dict(threadId='test_id', userId='11111111', _id='some_random_id', lastPostId='1234')
    ]
    MOCK_USER_ATTRSET = [
        dict(userId='11111111', name='Alan', _id='some_random_id'),
        dict(userId='33333333', name='Bobby', _id='some_random_id'),
    ]
    MOCK_POST_ATTRSET = [
        dict(postId='1234', userId='33333333'),
        dict(postId='3456', userId='33333333'),
        dict(postId='4567', userId='33333333'),
    ]
    MOCK_SEARCHFILTER = 'test_search_filter'
    MOCKPAGING_DEFAULT_RETURN = 'default_paging'

    @pytest.fixture(scope='function', autouse=True)
    def setDefaultReturnValues(self, service):
        mock_threads = create_mock_entities(self.MOCK_THREAD_ATTRSET)
        threads_from_repo = create_return_from_repo(mock_threads, 'threads')
        mock_users = create_mock_entities(self.MOCK_USER_ATTRSET)
        users_from_repo = create_return_from_repo(mock_users, 'users')
        mock_posts = create_mock_entities(self.MOCK_POST_ATTRSET)
        posts_from_repo = create_return_from_repo(mock_posts, 'posts')

        service._repo.searchThread.return_value = threads_from_repo
        service._repo.searchUser.return_value = users_from_repo
        service._repo.searchPost.return_value = posts_from_repo
        service._searchFilterCreator.create_threadsearch.return_value = self.MOCK_SEARCHFILTER
        service._paging.return_value = self.MOCKPAGING_DEFAULT_RETURN

    def test_searchThreadByExplicitIdPassesThreadIdToSearchFilterCreator(self, service):
        creator = service._searchFilterCreator
        expected_arg = dict(threadId=self.DEFAULT_THREAD_ID)

        service.searchThreadByExplicitId(self.DEFAULT_THREAD_ID)

        assert len(creator.create_threadsearch.call_args_list) > 0
        passed_arg, *_ = creator.create_threadsearch.call_args_list[0][0]
        assert passed_arg == expected_arg

    def test_searchThreadByExplicitIdPassesSearchFilterToRepo(self, service):
        repo = service._repo

        service.searchThreadByExplicitId(self.DEFAULT_THREAD_ID)

        assert len(repo.searchThread.call_args_list) > 0
        passed_filter, *_ = repo.searchThread.call_args_list[0][0]
        assert passed_filter == self.MOCK_SEARCHFILTER

    def test_searchThreadByExplicitIdShouldPassKeyValuesToPaging(self, service):
        mockPaging = service._paging

        service.searchThreadByExplicitId(self.DEFAULT_THREAD_ID)

        mockPaging.assert_called_with()

    def test_searchThreadByExplicitIdPassesSearchFilterToUpdate(self, service):
        repo = service._repo

        service.searchThreadByExplicitId(self.DEFAULT_THREAD_ID)

        assert repo.updateThread.call_count == 1
        passed_filter, *_ = repo.updateThread.call_args_list[0][0]
        assert passed_filter == self.MOCK_SEARCHFILTER

    def test_searchThreadByExplicitIdShouldUpdateThreadViewCount(self, service):
        mockRepo = service._repo

        service.searchThreadByExplicitId(self.DEFAULT_THREAD_ID)

        assert mockRepo.updateThread.call_count == 1
        _, update = mockRepo.updateThread.call_args[0]
        assert getattr(update, 'increment') == 'views'

    def test_searchThreadByExplicitIdShouldGenerateSearchForOwnerUser(self, service):
        mockRepo = service._repo
        owner_ids = [ attrs['userId'] for attrs in self.MOCK_THREAD_ATTRSET ]
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='userId',
            operator='eq',
            value=owner_ids
        ))

        service.searchThreadByExplicitId(self.DEFAULT_THREAD_ID)

        assert len(mockRepo.searchUser.call_args_list)
        passed_filter, *_ = mockRepo.searchUser.call_args_list[0][0]
        assert passed_filter == expected_filter

    def test_searchThreadsByExplicitIdShouldNotSearchForLastPostOrOwnerWhenNoThreadReturned(self, service):
        repo = service._repo
        repo.searchThread.return_value = create_return_from_repo([], 'threads')

        service.searchThreadByExplicitId(self.DEFAULT_THREAD_ID)

        assert repo.searchUser.call_count == 0
        assert repo.searchPost.call_count == 0

    def test_searchThreadByExplicitIdShouldReturnSearchResult(self, service):
        expected_thread = self.MOCK_THREAD_ATTRSET[0]
        
        result = service.searchThreadByExplicitId(self.DEFAULT_THREAD_ID)

        assert result['returnCount'] == 1
        assert result['matchedCount'] == 1
        threads = result['threads']
        assert len(threads) == 1
        for k, v in expected_thread.items():
            assert getattr(threads[0], k) == v

    def test_searchThreadByExplicitIdShouldReturnOwnerUser(self, service):
        expected_user = self.MOCK_USER_ATTRSET[0]
        
        result = service.searchThreadByExplicitId(self.DEFAULT_THREAD_ID)

        thread = result['threads'][0]
        owner = getattr(thread, 'owner')
        assert len(owner) == 1
        for k, v in expected_user.items():
            assert getattr(owner[0], k) == v

    def test_searchThreadByExplicitIdShouldContainLastPostInfo(self, service):
        expected_lastpost_attrs = self.MOCK_POST_ATTRSET[0]

        result = service.searchThreadByExplicitId(self.DEFAULT_THREAD_ID)

        thread = result['threads'][0]
        lastposts = getattr(thread, 'lastPost')
        assert len(lastposts) == 1
        for k, v in expected_lastpost_attrs.items():
            assert getattr(lastposts[0], k) == v

    def test_searchThreadByExplicitIdShouldHaveEmptyLastpostsWhenNoMatchingPostFound(self, service):
        repo = service._repo
        thread_attrset = [
            dict(threadId='test_id1', userId='test_user1', lastPostId='nonexistant_id'),
            dict(threadId='test_id2', userId='test_user1', lastPostId='nonexistant_id'),
            dict(threadId='test_id3', userId='test_user1', lastPostId='nonexistant_id'),
        ]
        mock_threads = create_mock_entities(thread_attrset)
        repo.searchThread.return_value = create_return_from_repo(mock_threads, 'threads')

        result = service.searchThreadByExplicitId(self.DEFAULT_THREAD_ID)

        for thread in result['threads']:
            lastposts = getattr(thread, 'lastPost')
            assert len(lastposts) == 0


class TestSearchBoardByKeyValues:
    MOCK_BOARD_ATTRSET = [
        dict(boardId='test_id', userId='11111111', _id='some_random_id', )
    ]
    MOCK_USER_ATTRSET = [
        dict(userId='11111111', name='Alan', _id='some_random_id'),
        dict(userId='33333333', name='Bobby', _id='some_random_id'),
    ]

    @pytest.fixture(scope='function', autouse=True)
    def setDefaultReturnValues(self, service):
        mock_boards = create_mock_entities(self.MOCK_BOARD_ATTRSET)
        boards_from_repo = create_return_from_repo(mock_boards)
        mock_users = create_mock_entities(self.MOCK_USER_ATTRSET)
        users_from_repo = create_return_from_repo(mock_users)

        service._repo.searchBoard.return_value = boards_from_repo
        service._repo.searchUser.return_value = users_from_repo


# helper functions
def create_return_from_repo(entities, entity_name):
    return {
        entity_name: entities,
        'matchedCount': len(entities),
        'returnCount': len(entities),
    }
