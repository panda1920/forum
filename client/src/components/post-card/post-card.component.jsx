import React from 'react';

import Portrait from '../portrait/portrait.component';
import { convertEpochToLocalDateString } from '../../scripts/converter';

import './post-card.styles.scss';

const PostCard = ({ postnum, post }) => {
  const owner = post.owner[0];

  return (
    <div className='post-card'>

      <div className='post-card-ownerinfo'>
        <Portrait
          title='portrait image of owner user'
          imageUrl={owner.imageUrl}
        />
        <p>{ owner.displayName }</p>
      </div>

      <div className='post-card-content'>

        <div className='post-card-header'>
          <p className='post-card-header-postnum'>
            { `#${postnum}` }
          </p>
          <p className='post-card-header-postedat'>
            { `Posted at: ${convertEpochToLocalDateString(post.createdAt)}` }
          </p>
        </div>

        <hr />

        <div
          className='post-card-content'
          dangerouslySetInnerHTML={{ __html: post.content}}
        />

        <hr />

        <div className='post-card-footer'>
          <p>Placeholder footer</p>
        </div>

      </div>
      
    </div>
  );
};

export default PostCard;
