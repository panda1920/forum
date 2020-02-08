import React from 'react';

const TextInput = ({ label, ...otherProps }) => {
  return (
    <div className='textinput'>
      <div className='textinput-label'>
        {label}
      </div>
      <div className='textinput-input'>
        <input {...otherProps} />
      </div>
    </div>
  );
}

export default TextInput;