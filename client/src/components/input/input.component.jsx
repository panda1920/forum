import React from 'react';

const Input = ({ label, ...otherProps}) => {
  return (
    <div className='input'>
      <div className='label'>
        {label}
      </div>
      <div className='input-input'>
        <input {...otherProps} />
      </div>
    </div>
  );
}

export default Input;