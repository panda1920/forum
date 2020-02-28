import React from 'react';

import './form-button.styles.scss';
import Button from '../button/button.component';

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