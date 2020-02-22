import React from 'react';

import Header from  '../../components/header/header.component';
import Footer from  '../../components/footer/footer.component';

import './base-page.styles.scss';

const BasePage = () => {
  return (
    <div className='base-page'>
      <Header />
      <div className='main-content'>
        
      </div>
      <Footer />
    </div>
  );
}

export default BasePage;
