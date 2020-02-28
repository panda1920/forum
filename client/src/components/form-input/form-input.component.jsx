import React from 'react';

import './form-input.styles.scss';

const FormInput = (props) => {
  const { className, ...otherProps } = props;
  return (
    <input className={`form-input ${convertClassNameToString(className)}`} {...otherProps} />
  );
}

function convertClassNameToString(className) {
  return className ? className : '';
}

export default FormInput;