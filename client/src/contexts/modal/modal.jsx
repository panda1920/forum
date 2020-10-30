import React, { useState, createContext } from 'react';

const ModalContextInitialValues = {
  isSignupOpen: false,
  isLoginOpen: false,
  toggleSignup: () => {},
  toggleLogin: () => {},
};

export const ModalContext = createContext(ModalContextInitialValues);

export const ModalContextProvider = ({ children, toggleBlur }) => {
  const [ isSignupOpen, setIsSignupOpen ] = useState(false);
  const [ isLoginOpen, setIsLoginOpen ] = useState(false);
  const toggleSignup = () => {
    toggleBlur();
    setIsSignupOpen(!isSignupOpen);
  };
  const toggleLogin = () => {
    toggleBlur();
    setIsLoginOpen(!isLoginOpen);
  };

  return (
    <ModalContext.Provider
      value={{ isSignupOpen, isLoginOpen, toggleSignup, toggleLogin }}
    >
      { children }
    </ModalContext.Provider>
  );
};