import React, { useContext, useEffect } from 'react';
import ReactModal from 'react-modal';

import { ModalContext } from '../../contexts/modal/modal';

import './modal-login.styles.scss';


const ModalLogin = () => {
  const { isLoginOpen, toggleLogin } =  useContext(ModalContext);
  // initial setup of modal
  useEffect(() => {
    ReactModal.setAppElement('#root');
  });

  return (
    <ReactModal
      isOpen={isLoginOpen}
      onRequestClose={toggleLogin}
      className='modal'
      overlayClassName='modal-overlay'
      portalClassName='ReactModalPortal-Login'
      contentLabel='modal-login'
    >
      <div title='modal-login'>
        <p>Signin</p>
        <p>Signin</p>
        <p>Signin</p>
        <p>Signin</p>
        <p>Signin</p>
        <p>Signin</p>
        <p>Signin</p>
        <p>Signin</p>
      </div>

    </ReactModal>
  );
}

export default ModalLogin;