import React, { useState } from 'react';

import Header from  '../../components/header/header.component';
import Footer from  '../../components/footer/footer.component';
import { ModalContextProvider } from '../../contexts/modal/modal';
import ModalLogin from '../../components/modal-login/modal-login.component';
import ModalSignup from '../../components/modal-signup/modal-signup.component';

import './base-page.styles.scss';

const BasePage = () => {
  const [ isBlurred, setBlur ] = useState(false);
  const getBlurClass = () => isBlurred ? 'blurred' : 'hello';
  const toggleBlur = () => setBlur(!isBlurred);

  return (
    <div className={`base-page ${getBlurClass()}`}>
      <ModalContextProvider toggleBlur={toggleBlur}>
        <ModalLogin />
        <ModalSignup />
        <Header />
        <div className='main-content'>
          
        </div>
        <Footer />
      </ModalContextProvider>
    </div>
  );
}

export default BasePage;
