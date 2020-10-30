import React from 'react';

import './block-text.styles.scss';

const BlockText = ({ children, className }) => {
  return (
    <div className={`block-text ${className ? className : ''}`}>
      {children}
    </div>
  );
}

export default BlockText;