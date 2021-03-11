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
    const url = `${paths.userApi}/${userId}/update-portrait`;
    const formData = new FormData();
    formData.set('portraitImage', file);
    
    return apiCall(
        url,
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
    const customHeader = { ...headers, 'X-Requested-With': 'myapp' };
    try {
        let response = await fetch(url, {
            method, headers: customHeader, body, credentials: 'same-origin'
        });

        return (
            (response.status >= 500)
            // ignore all server side error because there is nothing that can be done
            ? createDummyResponseForError()
            : response
        );
    }
    catch(err) {
        // do nothing when fetch api fails
        // failure is normally due to some connection issues
        console.log(err);
        return createDummyResponseForError();
    }
}

function createDummyResponseForError() {
    // notify that info from server side is ignored
    return { ignore: true, ok: false };
}

function createQueryString(object) {
    return Object.keys(object)
        .map(key => encodeURIComponent(key) + '=' + encodeURIComponent(object[key]))
        .join('&');
}
