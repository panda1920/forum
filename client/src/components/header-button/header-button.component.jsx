import React from 'react';

import './header-button.styles.scss';

const HeaderButton = ({ children, className, onClick }) => {
  return (
    <div className={`${className} header-button`} onClick={onClick}>
      { children }
    </div>
  );
}

export default HeaderButton;