import React from 'react';
import { BrowserRouter, Switch, Route } from 'react-router-dom';

import BasePage from './pages/base/base.component';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <BasePage />
      </div>
    </BrowserRouter>
  );
}

export default App;
