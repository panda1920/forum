import { createContext } from 'react';

const UsersContext = createContext({
    users: [],
    fetchUsers: () => {},
});

export default UsersContext;