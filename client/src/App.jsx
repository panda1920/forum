import React from 'react';
import { BrowserRouter, Switch, Route } from 'react-router-dom';

import Threads from './components/threads/threads.component';
import UsersPage from './pages/users/userspage';
import PostsPage from './pages/posts/postspage';
import Signup from './components/signup/signup.component';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Switch>
          <Route path='/users' component={UsersPage} />
          <Route path='/posts' component={PostsPage} />
          <Route path='/signup' component={Signup} />
          <Route path='/' component={Threads} />
        </Switch>
      </div>
    </BrowserRouter>
  );
}

export default App;
