import React from 'react';
import { BrowserRouter } from 'react-router-dom';

import BasePage from './pages/base/base-page.component';

import { CurrentUserContextProvider } from './contexts/current-user/current-user';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <CurrentUserContextProvider>
          <BasePage />
        </CurrentUserContextProvider>
      </div>
    </BrowserRouter>
  );
}

export default App;
