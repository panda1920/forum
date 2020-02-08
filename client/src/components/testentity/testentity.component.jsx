import React from 'react';

import ClearButton from '../clearButton/clearButton.component';

import './testentity.style.scss';

const TestEntity = ({ entity, id, apiPath, refresh } ) => {
  const { content, ...inlineProps } = entity;
  let propList = []
  for (let prop in inlineProps) {
    propList.push({ prop, value: entity[prop] });
  }
  
  return (
    <div className='testentity-container'>
      <div className='clearbutton-container'>
        <ClearButton id={id} path={apiPath} refresh={refresh}/>
      </div>
      <div className='testentity'>
        <div className='testentity-display'>
          {
            propList.map(prop => {
              return <p key={prop.prop}>{prop.prop}: {prop.value}</p>
            })
          }
          <div dangerouslySetInnerHTML={{ __html: content }}/>
        </div>
      </div>
    </div>
  );
}

export default TestEntity;