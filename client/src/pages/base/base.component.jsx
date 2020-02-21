import React from 'react';

import Header from  '../../components/header/header.component';
import Footer from  '../../components/footer/footer.component';

import './base.styles.scss';

const BasePage = () => {
  return (
    <div className='base-page'>
      <Header id='header'/>
      <div className='main-content'>
        
      </div>
      <Footer />
    </div>
  );
}

export default BasePage;