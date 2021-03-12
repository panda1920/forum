import React, { useContext } from 'react';

import Portrait from '../portrait/portrait.component';
import { CurrentUserContext } from '../../contexts/current-user/current-user';

import { updateUserPortrait } from '../../scripts/api';

const ProfileFieldPortrait = (props) => {
  const { imageUrl } = props;
  const { userId } = useContext(CurrentUserContext);

  const onChangeHandler = async (e) => {
    const file = e.target.files[0];

    await updateUserPortrait({ userId, file });
  };

  return (
    <div className='profile-field-portrait'>
      <Portrait imageUrl={imageUrl} />
      <input
        type='file'
        alt='image-input'
        onChange={onChangeHandler}
      />
    </div>
  );
};

export default ProfileFieldPortrait;
