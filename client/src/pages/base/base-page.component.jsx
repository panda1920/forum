import React, { useReducer } from 'react';

import Header from  '../../components/header/header.component';
import Footer from  '../../components/footer/footer.component';
import ModalLogin from '../../components/modal-login/modal-login.component';
import ModalSignup from '../../components/modal-signup/modal-signup.component';

import { ModalContextProvider } from '../../contexts/modal/modal';
import { CurrentUserContextProvider } from '../../contexts/current-user/current-user';

import './base-page.styles.scss';

const reducer = (state, action) => {
  switch (action.type) {
    case 'toggleBlur':
      return { ...state, isBlurred: !state.isBlurred };
    default:
      console.log(`unknown action type: ${action.type}`);
      return state;
  }
}

const BasePage = () => {
  const [ state, dispatch ] = useReducer(reducer, { isBlurred: false });
  const getBlurClass = () => state.isBlurred ? 'blurred' : '';
  const toggleBlur = () => dispatch({ type: 'toggleBlur' });

  return (
    <div className={`base-page ${getBlurClass()}`}>
      <CurrentUserContextProvider>
        <ModalContextProvider toggleBlur={toggleBlur}>
          <ModalLogin />
          <ModalSignup />
          <Header />
          <div className='main-content'>
            
          </div>
          <Footer />
        </ModalContextProvider>
      </CurrentUserContextProvider>
    </div>
  );
}

export default BasePage;
