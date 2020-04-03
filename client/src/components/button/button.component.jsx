import React from 'react';

import './button.styles.scss';

class Button extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      clickedRecently: false,
      timerTaskId: null,
    };
  }

  // prevent click being triggered rapidly
  onClickHandler() {
    const { clickedRecently } = this.state;
    const { onClick } = this.props;
    
    if (clickedRecently)
      return;
    
    onClick();
    this.setState({ clickedRecently: true });
    this.resetClickedRecentlyLater();
  }

  resetClickedRecentlyLater() {
    const id = setTimeout(() => {
      this.setState({ clickedRecently: false });
    }, 200);
    this.setState({ timerTaskId: id });
  }

  // unregister async task to update component state because button will unmount
  componentWillUnmount() {
    const { timerTaskId } = this.state;

    clearTimeout(timerTaskId);
  }

  render() {
    const { className, onClick, children, ...otherProps } = this.props;
    const testid = this.props['data-testid'];
    const classes = convertClassNamePropToString(className);
    const onClickHandlerCallback = () => { this.onClickHandler(); };

    return (
      <div
        className={`button ${classes}`}
        onClick={onClickHandlerCallback}
        data-testid={testid}
        {...otherProps}
      >
        { children }
      </div>
    );
  }
}

const convertClassNamePropToString = (className) => {
  return (className ? `${className}` : '');
};

export default Button;