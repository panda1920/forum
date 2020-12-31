import React, { createContext, useState, useCallback } from 'react';

export const INITIAL_STATE = {
    userId: '0',
    userName: 'anoynymous',
    displayName: 'anonymous',
    imageUrl: '',
    beforeFetch: true,
    setCurrentUser: () => {},
    isLoggedin: () => {},
};

export const CurrentUserContext = createContext(INITIAL_STATE);

export const CurrentUserContextProvider = ({ children }) => {
  const [ userId, setUserId ] = useState('');
  const [ userName, setUserName ] = useState('');
  const [ displayName, setDisplayName ] = useState('');
  const [ imageUrl, setImageUrl ] = useState('');
  const [ beforeFetch, setBeforeFetch ] = useState(true);

  const setCurrentUser = useCallback((user) => {
    const { userId, userName, displayName, imageUrl } = user;
    setUserId(userId);
    setUserName(userName);
    setDisplayName(displayName);
    setImageUrl(imageUrl);
    setBeforeFetch(false);
  }, []);

  const isLoggedin = useCallback(() => {
    const isUserIdAnonymous = userId === '0';
    return !(beforeFetch || isUserIdAnonymous);
  }, [userId, beforeFetch]);

  return (
    <CurrentUserContext.Provider
      value={{
        userId, userName, displayName, imageUrl, beforeFetch, setCurrentUser, isLoggedin,
      }}
    >
      { children }
    </CurrentUserContext.Provider>
  );
};
