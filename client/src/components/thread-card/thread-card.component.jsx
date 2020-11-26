import React from 'react';

import BlockText from '../block-text/block-text.component';
import Portrait from '../portrait/portrait.component';
import { convertEpochToLocalDateString } from '../../scripts/converter';

import './thread-card.styles.scss';

const ThreadCard = ({ thread }) => {
  const owner = thread.owner[0];

  return (
    <div title='thread card' className='thread-card'>
      <div className='thread-card-title-userinfo'>
        <BlockText className='thread-card-title'>{thread.title}</BlockText>
        <BlockText className='thread-card-userinfo'>
          Created by {owner.displayName},&nbsp;
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
          <BlockText>{thread.posts}</BlockText>
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
