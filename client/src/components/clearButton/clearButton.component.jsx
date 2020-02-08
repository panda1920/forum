import React from 'react';

import { createDeleteApiPath } from '../../paths';

import './clearButton.style.scss';

const ClearButton = ({ path, id, refresh }) => {
  return (
    <div className='clearbutton' onClick={ deleteEntity(path, id, refresh) }>
      X
    </div>
  );
}

const deleteEntity = (path, id, refresh) => {
  return (event) => {
    const method = 'DELETE';
    const url = createDeleteApiPath(path, id);
    
    fetch(url, { method })
    .then(response => {
      if (response.ok) {
        console.log('Delete success');
        refresh();
      }
      else
        console.log('Delete failed!');
    })
    .catch(error => {
      console.log(error);
    });
  };
}

export default ClearButton;