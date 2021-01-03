import React from 'react';
import ErrorText from '../error-text/error-text.component';

import './form-input.styles.scss';

const FormInput = (props) => {
  // don't want to pass className to child here
  const { errorMsg, className, ...otherProps } = props;
  return (
    <div className={computeClass(props)}>
      <input className={computeInputClass(props)} {...otherProps} />
      { errorMsg ? <ErrorText text={errorMsg} /> : null }
    </div>
  );
}

function computeClass(props) {
  const { className, } = props;
  let classString = 'form-input';
  classString += className ? ` ${className}` : '';

  return classString;
}

function computeInputClass(props) {
  const { inputClassName, errorMsg } = props;
  let classString = inputClassName ? ` ${inputClassName}` : '';
  classString += errorMsg ? ' error-border' : '';

  return classString;
}

export default FormInput;
