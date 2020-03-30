import React, { useReducer, useEffect, useContext, useCallback } from 'react';

import Header from  '../../components/header/header.component';
import Footer from  '../../components/footer/footer.component';
import ModalLogin from '../../components/modal-login/modal-login.component';
import ModalSignup from '../../components/modal-signup/modal-signup.component';

import { ModalContextProvider } from '../../contexts/modal/modal';
import { CurrentUserContext } from '../../contexts/current-user/current-user';
import { getSessionUser } from '../../scripts/api';

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
  const { setCurrentUser } = useContext(CurrentUserContext);
  
  const getBlurClass = () => state.isBlurred ? 'blurred' : '';
  const toggleBlur = useCallback( () => dispatch({ type: 'toggleBlur' }), []);

  useEffect(() => {
    const initSessionUser = async () => {
      const response = await getSessionUser();
      if (!response.ok)
        return;
  
      const { sessionUser } = await response.json();
      setCurrentUser(sessionUser);
    }
    initSessionUser();
  }, []);

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
