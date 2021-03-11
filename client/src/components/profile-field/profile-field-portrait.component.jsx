import React from 'react';

import Portrait from '../portrait/portrait.component';

const ProfileFieldPortrait = (props) => {
  const { imageUrl } = props;
  return (
    <div className='profile-field-portrait'>
      <Portrait imageUrl={imageUrl} />
      <input type='image' alt='image-input' />
    </div>
  );
}

export default ProfileFieldPortrait;
