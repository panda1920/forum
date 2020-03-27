import React, { createContext, useState, useCallback } from 'react';

const INITIAL_STATE = {
    userId: '0',
    userName: 'anoynymous',
    displayName: 'anonymous',
    imageUrl: '',
    setCurrentUser: () => {},
    isLoggedin: () => {},
};

export const CurrentUserContext = createContext(INITIAL_STATE);

export const CurrentUserContextProvider = ({ children }) => {
  const [ userId, setUserId ] = useState('');
  const [ userName, setUserName ] = useState('');
  const [ displayName, setDisplayName ] = useState('');
  const [ imageUrl, setImageUrl ] = useState('');

  const setCurrentUser = (user) => {
    const { userId, userName, displayName, imageUrl } = user;
    setUserId(userId);
    setUserName(userName);
    setDisplayName(displayName);
    setImageUrl(imageUrl);
  }

  const isLoggedin = useCallback(() => {
    return (userId !== '') && (userId !== '0');
  }, [userId]);

  return (
    <CurrentUserContext.Provider
      value={{ userId, userName, displayName, imageUrl, setCurrentUser, isLoggedin }}
    >
      { children }
    </CurrentUserContext.Provider>
  );
}
