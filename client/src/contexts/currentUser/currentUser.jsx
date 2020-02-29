import { createContext, useState } from 'react';

const INITIAL_STATE = {
    userId: '0',
    imageURL: '',
    userName: 'anoynymous',
    displayName: 'anonymous',
    setCurrentUser: () => {},
};

export const CurrentUserContext = createContext(INITIAL_STATE);