import React from 'react';

import BlockText from '../block-text/block-text.component';
import Portrait from '../portrait/portrait.component';

import './thread-card.styles.scss';

const ThreadCard = ({ thread }) => {
  const owner = thread.owner[0];

  return (
    <div title='thread card' className='thread-card'>
      <div className='thread-card-title-userinfo'>
        <BlockText className='thread-card-title'>{thread.title}</BlockText>
        <BlockText className='thread-card-userinfo'>
          Created by {owner.displayName},&nbsp;
          {convertEpochToString(thread.createdAt)}
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
        <BlockText>{convertEpochToString(lastPost.createdAt)}</BlockText>
        <BlockText>{lastOwner.displayName}</BlockText>
      </div>
    </div>
  );
}

const convertEpochToString = (epochTime) => {
  const date = new Date(epochTime * 1000);
  const day = date.getUTCDate().toString().padStart(2, '0');
  const month = (date.getUTCMonth() + 1).toString().padStart(2, '0'); // utc month is 0-11
  const year = date.getUTCFullYear().toString();
  const hour = date.getUTCHours().toString().padStart(2, '0');
  const minute = date.getUTCMinutes().toString().padStart(2, '0');
  const second = date.getUTCSeconds().toString().padStart(2, '0');

  return `${day}/${month}/${year}, ${hour}:${minute}:${second}`;
};

export default ThreadCard;
