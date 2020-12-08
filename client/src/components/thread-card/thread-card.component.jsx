import React from 'react';
import { Link } from 'react-router-dom';

import BlockText from '../block-text/block-text.component';
import Portrait from '../portrait/portrait.component';

import { convertEpochToLocalDateString } from '../../scripts/converter';
import { clientThreadPath } from '../../paths';

import './thread-card.styles.scss';

const ThreadCard = ({ thread }) => {
  const owner = thread.owner[0];

  return (
    <div title='thread card' className='thread-card'>
      <div className='thread-card-title-userinfo'>
        <BlockText>
          <Link
            className='thread-card-title'
            to={{
              pathname: `${clientThreadPath}/${thread.threadId}`,
              state: { thread },
            }}
          >
            { thread.title }
          </Link>
        </BlockText>
        <BlockText className='thread-card-userinfo'>
          Created by {owner.displayName} at&nbsp;
          {convertEpochToLocalDateString(thread.createdAt)}
        </BlockText>
      </div>
      <div className='thread-card-views-posts'>
        <div className='views-posts'>
          <BlockText>Views:</BlockText>
          <BlockText>Posts:</BlockText>
        </div>
        <div className='views-posts-values'>
          <BlockText>{thread.views}</BlockText>
          <BlockText>{thread.postCount}</BlockText>
        </div>
      </div>
      { displayLastPost(thread) }
    </div>
  );
};

const displayLastPost = (thread) => {
  const lastPost = thread.lastPost[0];
  const lastOwner = lastPost.owner[0];

  return (
    <div className='thread-card-lastpost'>
      <Portrait
        imageUrl={lastOwner.imageUrl}
        title='last post portrait'
      />
      <div>
        <BlockText>{convertEpochToLocalDateString(lastPost.createdAt)}</BlockText>
        <BlockText>{lastOwner.displayName}</BlockText>
      </div>
    </div>
  );
}
export default ThreadCard;
