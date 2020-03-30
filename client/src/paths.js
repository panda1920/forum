// This is where I dump all my path information
// So it can be referred elsewhere on the client side code.

export const apiBasePath = '/v1';

export const userApi = apiBasePath + '/users';

export const userApiCreate = userApi + '/create';

export const userApiLogin = userApi + '/login';

export const userApiLogout = userApi + '/logout';

export const userApiSession = userApi + '/session';

// apiPath: userAPi, postsApi etc
// id: id of entity to Delete
export const createDeleteApiPath = (apiPath, id) => {
    return `${apiPath}/${id}/delete`;
}

// apiPath: userAPi, postsApi etc
// id: id of entity to Update
export const createUpdateApiPath = (apiPath, id) => {
    return `${apiPath}/${id}/update`;
}

export const postApi = apiBasePath + '/posts';

export const postApiCreate = postApi + '/create';