import React, { useState, useCallback, useEffect } from 'react';

import './button.styles.scss';

const Button = (props) => {
  const { className, onClick, children, ...otherProps  } = props;
  const [ clickedRecently, setClickedRecently ] = useState(false);
  const [ timerTaskId, setTimerTaskId ] = useState(null);
  
  const testid = props['data-testid'];
  const classes = convertClassNamePropToString(className);

  const resetClickedRecentlyLater = () => {
    const id = setTimeout(() => {
      setClickedRecently(false);
    }, 200);
    setTimerTaskId(id);
  };

  // prevents onclick triggering too often
  const onClickHandler = useCallback(() => {
    if (clickedRecently)
      return;
    
    onClick();
    setClickedRecently(true);
    resetClickedRecentlyLater();

  }, [clickedRecently, onClick]);
  
  useEffect(() => {
    return () => {
      setClickedRecently(false);
      clearTimeout(timerTaskId);
    };
  });

  return (
    <div
      className={`button ${classes}`}
      onClick={onClickHandler}
      data-testid={testid}
      {...otherProps}
    >
      { children }
    </div>
  );
};

const convertClassNamePropToString = (className) => {
  return (className ? `${className}` : '');
};

export default Button;