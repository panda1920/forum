import React from 'react';
import { BrowserRouter, Switch, Route } from 'react-router-dom';

import Threads from './components/threads/threads.component';
import Users from './components/users/users.component';
import Signup from './components/signup/signup.component';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Switch>
          <Route path='/users' component={Users} />
          <Route path='/signup' component={Signup} />
          <Route path='/' component={Threads} />
        </Switch>
      </div>
    </BrowserRouter>
  );
}

export default App;
