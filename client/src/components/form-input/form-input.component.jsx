import React from 'react';
import BlockText from '../block-text/block-text.component';

import './form-input.styles.scss';

const FormInput = (props) => {
  const { className, errorMsg, ...otherProps } = props;
  return (
    <div className='form-input-container'>
        <input className={computeClass(props)} {...otherProps} />
        {
          <BlockText className='form-input-error'>{errorMsg}</BlockText>
        }
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