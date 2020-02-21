import React from 'react';

import './header-button.styles.scss';

const HeaderButton = ({ children, className }) => {
  console.log(className);
  return (
    <div className={`${className} header-button`}>
      { children }
    </div>
  );
}

export default HeaderButton;