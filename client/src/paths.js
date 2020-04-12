// This is where I dump all my path information
// So it can be referred elsewhere on the client side code.

// apiPath: userAPi, postsApi etc
// id: id of entity to Delete
export const createCreateApiPath = (apiPath) => {
    return `${apiPath}/create`;
};

export const createDeleteApiPath = (apiPath, id) => {
    return `${apiPath}/${id}/delete`;
};

export const createUpdateApiPath = (apiPath, id) => {
    return `${apiPath}/${id}/update`;
};

export const apiBasePath = '/v1';

export const userApi = apiBasePath + '/users';

export const userApiCreate = userApi + '/create';

export const userApiLogin = userApi + '/login';

export const userApiLogout = userApi + '/logout';

export const userApiSession = userApi + '/session';


export const postApi = apiBasePath + '/posts';

export const threadApi = apiBasePath + '/threads';
