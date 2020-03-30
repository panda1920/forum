// here I put all api call related code made from frontend

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
        paths.userApiLogin,
        'POST',
        { 'Content-Type': 'application/json' },
        JSON.stringify({ userName: email, password }),
    );
}

export function getSessionUser() {
    return apiCall(
        paths.userApiSession,
        'GET',
    );
}

async function apiCall(url, method, headers, body) {
    try {
        let response = await fetch(url, { method, headers, body });
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