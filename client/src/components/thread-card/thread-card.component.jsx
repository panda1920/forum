import React from 'react';

import BlockText from '../block-text/block-text.component';
import Portrait from '../portrait/portrait.component';

import './thread-card.styles.scss';

const ThreadCard = ({ thread }) => {
  return (
    <div title='thread card' className='thread-card'>
      <BlockText className='thread-card-title'>{thread.title}</BlockText>
      <BlockText className='thread-card-userinfo'>
        <Portrait
          imageUrl={thread.owner.imageUrl}
          alt='owner portrait'
        />&nbsp;
        {thread.owner.displayName}&nbsp;
        Created at {convertEpochToString(thread.createdAt)}
      </BlockText>
      <BlockText className='thread-card-views'>Views: {thread.views}</BlockText>
      <BlockText className='thread-card-posts'>Posts: {thread.posts}</BlockText>
    </div>
  );
};

const convertEpochToString = (epochTime) => {
  return new Date(epochTime * 1000).toUTCString()
};

export default ThreadCard;