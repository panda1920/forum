import React from 'react';

import BlockText from '../block-text/block-text.component';

import './error-text.styles.scss';

const ErrorText = ({ text, className }) => {
  if (!text)
    return null;

  className = className ? `error-text ${className}`: 'error-text';

  return (
    <BlockText className={className}>
      { `Error: ${text}` }
    </BlockText>
  );
};

export default ErrorText;
