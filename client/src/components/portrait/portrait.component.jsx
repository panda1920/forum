import React from 'react';

import './portrait.styles.scss';

const Portrait = ({ imageUrl, className, ...otherProps }) => {
  const inlinePortraitStyle = {
    backgroundImage: `url(${imageUrl})`,
    backgroundSize: 'contain',
    backgroundPosition: 'center',
  };
  const classes = `portrait ${className ? className : ''}`;

  return (
    <div
      className={classes}
      style={inlinePortraitStyle}
      {...otherProps}
    >
    </div>
  );
}

export default Portrait;