// here I put all api calls to backend

import * as paths from '../paths';

export function login(email, password) {
    return apiCall(
        paths.userApiLogin,
        'POST',
        { 'Content-Type': 'application/json' },
        JSON.stringify({ userName: email, password }),
    );
}

export function logout() {
    return apiCall(
        paths.userApiLogout,
        'POST',
    );
}

export function signup(email, password) {
    return apiCall(
        paths.userApiCreate,
        'POST',
        { 'Content-Type': 'application/json' },
        JSON.stringify({ userName: email, password }),
    );
}

export function updateUser(fields) {
    const { userId, ...rest } = fields;

    return apiCall(
        `${paths.userApi}/${userId}/update`,
        'PATCH',
        { 'Content-Type': 'application/json' },
        JSON.stringify(rest),
    );
}

export function updateUserPortrait(fields) {
    const { userId, file } = fields;
    const formData = new FormData();
    formData.set('file', file);
    
    return apiCall(
        `${paths.userApi}/${userId}/update`,
        'PATCH',
        {},
        formData,
    );
}

export function getSessionUser() {
    return apiCall(
        paths.userApiSession,
        'GET',
    );
}

export function verifyCredentials(credentials) {
    const { userId, ...rest } = credentials;
    return apiCall(
        `${paths.userApi}/${userId}/confirm`,
        'POST',
        { 'Content-Type': 'application/json' },
        JSON.stringify(rest),
    );
}

export function searchThreads(criteria) {
    const url = `${paths.threadApi}?${createQueryString(criteria)}`;
    return apiCall(
        url,
        'GET',
    );
}

export function viewThread(threadId) {
    const url = `${paths.threadApi}/${threadId}/view`;
    return apiCall(
        url,
        'PATCH',
    );
}

export function createThread(newThread) {
    const url = `${paths.createCreateApiPath(paths.threadApi)}`;
    return apiCall(
        url, 'POST', { 'Content-Type': 'application/json' }, JSON.stringify(newThread)
    );
}

export function searchPosts(criteria) {
    const url = `${paths.postApi}?${createQueryString(criteria)}`;
    return apiCall(
        url,
        'GET',
    );
}

export function createPost(newPost) {
    const url = `${paths.createCreateApiPath(paths.postApi)}`;
    return apiCall(
        url, 'POST', { 'Content-Type': 'application/json' }, JSON.stringify(newPost)
    );
}

export function searchBoards(criteria) {
    const url = `${paths.boardApi}?${createQueryString(criteria)}`;
    return apiCall(
        url,
        'GET',
    );
}

async function apiCall(url, method, headers, body) {
    // add custom header to force trigger CORS preflight
    const custom_header = { ...headers, 'X-Requested-With': 'myapp' };
    try {
        let response = await fetch(url, { method, headers: custom_header, body, credentials: 'same-origin' });
        return defaultResponseHandler(response);
    }
    catch(err) {
        // do nothing when fetch api fails
        // failure is normally due to some connection issues
        console.log(err);
    }
}

async function defaultResponseHandler(response) {
    // ignore all server side error
    if (response.status >= 500)
        return { ignore: true, ok: false };
    else
        return response;
}

function createQueryString(object) {
    return Object.keys(object)
        .map(key => encodeURIComponent(key) + '=' + encodeURIComponent(object[key]))
        .join('&');
}
