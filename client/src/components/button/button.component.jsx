import React from 'react';

import './button.styles.scss';

const Button = (props) => {
  const { className, onClick, children, ...otherProps  } = props;
  const testid = props['data-testid'];
  const classes = convertClassNamePropToString(className);
  return (
    <div
      className={`Button ${classes}`}
      onClick={onClick}
      data-testid={testid}
      {...otherProps}
    >
      { children }
    </div>
  );
}

const convertClassNamePropToString = (className) => {
  return (className ? `${className}` : '');
}

export default Button;