import { postApiCreate } from '../../paths';

import createDOMPurify from 'dompurify';

export const createInputHandler = (setContent) => {
    return (content, editor) => {
        setContent(content);
    };
};

export const createPostHandler = (content, refresh) => {
    return (event) => {
        event.preventDefault();
        let formdata = createFormdata(content);
        postContent(formdata, refresh);
    }
};

const createFormdata = (content) => {
    const randomId = ( Math.floor( Math.random() * 1000 ) + 10 ).toString();
    // want to do sanitization on server side eventually
    const sanitizedContent = createDOMPurify(window).sanitize(content);
    const formdata = new URLSearchParams();
    formdata.set('content', sanitizedContent);
    formdata.set('userId', '0');
    formdata.set('postId', randomId);
    
    return formdata;
}

const postContent = async (formdata, refresh) => {
    const method = 'POST';
    const headers = { 'Content-Type': 'application/x-www-form-urlencoded' };

    try {
        let response = await fetch(postApiCreate, { method, headers, body: formdata });
        if (response.ok) {
            console.log('Created post!');
            refresh();
        }
        else {
            console.log('Failed to create post!');
            let json = await response.json();
            console.log(json);
        }
    }
    catch (error) {
        console.log(error);
    }
}