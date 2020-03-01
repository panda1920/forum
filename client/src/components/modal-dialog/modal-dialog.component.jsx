import React, { useEffect } from 'react';
import ReactModal from 'react-modal';

import Button from '../button/button.component';

import './modal-dialog.styles.scss';

const ModalDialog = ({ isOpen, toggleOpen, title, children}) => {
  // initial setup of modal
  useEffect(() => {
    ReactModal.setAppElement('#root');
  }, []);

  return (
    <ReactModal
      isOpen={isOpen}
      onRequestClose={toggleOpen}
      className='modal'
      overlayClassName='modal-overlay'
      portalClassName='ReactModalPortal-Login'
      contentLabel={title}
    >
      <div title={title}>
        <Button
          className='modal-button-close'
          onClick={toggleOpen}
        >
          <i className='material-icons md-36' title='button-close'>close</i>
        </Button>
        {children}
      </div>

    </ReactModal>
  );
}

export default ModalDialog;