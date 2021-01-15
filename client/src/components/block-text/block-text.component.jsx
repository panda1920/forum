import React from 'react';

import './block-text.styles.scss';

const BlockText = (props) => {
  const { children, className, ...otherProps } = props;
  return (
    <div
      className={`block-text ${className ? className : ''}`}
      { ...otherProps }
    >
      {children}
    </div>
  );
}

export default BlockText;
