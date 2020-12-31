import React from 'react';
import ErrorText from '../error-text/error-text.component';

import './form-input.styles.scss';

const FormInput = (props) => {
  const { className, errorMsg, ...otherProps } = props;
  return (
    <div className='form-input'>
      <input className={computeClass(props)} {...otherProps} />
      { errorMsg ? <ErrorText text={errorMsg} /> : null }
    </div>
  );
}

function computeClass(props) {
  const { className, errorMsg } = props;
  let classString = 'form-input';
  classString += className ? ` ${className}` : '';
  classString += errorMsg ? ' error-border' : '';

  return classString;
}

export default FormInput;
