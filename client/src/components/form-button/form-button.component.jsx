import React from 'react';

import Button from '../button/button.component';

import './form-button.styles.scss';

const FormButton = ({ className, children, ...otherProps }) => {
  return (
    <Button
      className={`form-button ${className ? className: ''}`}
      {...otherProps}
    >
      {children}
    </Button>
  );
}

export default FormButton;
