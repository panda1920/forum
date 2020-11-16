import React, { useReducer, useEffect, useContext, useCallback } from 'react';
import { Switch, Route } from 'react-router-dom';

import BoardPage from '../board/board-page.component';
import ThreadPage from '../thread/thread-page';
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
};

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
    };
    initSessionUser();
  }, [setCurrentUser]);

  return (
    <div className={`base-page ${getBlurClass()}`}>
      <ModalContextProvider toggleBlur={toggleBlur}>
        <ModalLogin />
        <ModalSignup />
        <Header />
        <div className='main-content'>
          <Switch>
            <Route path='/sample'>
              <h1>SAMPLE</h1>
            </Route>
            <Route path='/thread/:threadId' component={ThreadPage} />
            <Route path='/'>
              <BoardPage boardId='0' />
            </Route>
          </Switch>
        </div>
        <Footer />
      </ModalContextProvider>
    </div>
  );
};

export default BasePage;
