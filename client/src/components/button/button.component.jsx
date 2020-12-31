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
  onClickHandler(e) {
    const { clickedRecently } = this.state;
    const { onClick } = this.props;
    if (!onClick)
      return;
    if (clickedRecently)
      return;
    
    this.executeAfterSettingFlag(() => onClick(e));
  }

  executeAfterSettingFlag(onClick) {
    const timerTaskId = setTimeout(() => {
      this.setState({ clickedRecently: false });
    }, 200);
    // need to invoke onClick as callback
    // because setstate would not immediatey update
    // if onClick is invoked on a separate line,
    // it may unmount the component before timerid is stored in state
    // which causes the above settimeout to run on a non-existant component
    this.setState({ clickedRecently: true, timerTaskId }, onClick);
  }

  // unregister async task to update component state because button will unmount
  componentWillUnmount() {
    const { timerTaskId } = this.state;

    clearTimeout(timerTaskId);
  }

  render() {
    const { className, children, onClick, ...otherProps } = this.props;
    // onClick here is needed to prevent it being forwarded to div element below
    const testid = this.props['data-testid'];
    const classes = convertClassNamePropToString(className);
    const onClickHandlerCallback = (e) => { this.onClickHandler(e); };

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
