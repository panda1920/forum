// logic for signup.component

export const changeSignupState = (setter) => {
    return (event) => {
        event.preventDefault();
        setter(event.target.value);
    };
}

export const createSubmitHandler = (state) => {
    const { username, password, cPassword, apiPath, refresh } = state;
    return (event) => {
      event.preventDefault();
      if (! validateInput(username, password, cPassword))
          return;
  
      createUser( createFormData(username, password), apiPath, refresh );
    };
}

const validateInput = (username, pw, cpw) => {
    if (pw !== cpw) {
        alert('Password must match');
        return false
    }

    if (!pw || !cpw) {
        alert('Make sure password is not empty');
        return false;
    }

    return true;
};

const createFormData = (username, password) => {
    const randomId = ( Math.floor( Math.random() * 1000 ) + 10 ).toString();
    let formdata = new URLSearchParams();
    formdata.set('userName', username);
    formdata.set('password', password);
    formdata.set('userId', randomId);
    return formdata;
};

const createUser = (body, apiPath, refresh) => {
    let method = 'POST';
    let headers = { 'Content-Type': 'application/x-www-form-urlencoded' };
    fetch(apiPath, { method, headers, body })
    .then(response => {
        if (response.ok) {
        console.log('Success!');
        // clearInputs();
        refresh();
        }
        else
        console.log('Failed to create user!');
    })
    .catch(error => {
        console.log(error)
    });
};

// const clearInputs = () => {
//     setUsername('');
//     setPw('');
//     setCpw('');
// };