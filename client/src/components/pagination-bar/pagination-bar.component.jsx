import React, { useCallback } from 'react';

import BlockText from '../block-text/block-text.component';
import Button from '../button/button.component';

import './pagination-bar.styles.scss';

const PaginationBar = ({ displayInfo, disableBack, disableNext, dispatch }) => {
  const firstHandler = useCallback(() => {
    dispatch({ type: 'firstPage' });
  }, [dispatch]);

  const backHandler = useCallback(() => {
    dispatch({ type: 'prevPage' });
  }, [dispatch]);

  const nextHandler = useCallback(() => {
    dispatch({ type: 'nextPage' });
  }, [dispatch]);

  const lastHandler = useCallback(() => {
    dispatch({ type: 'lastPage' });
  }, [dispatch]);

  return (
    <div title='pagination bar' className='pagination-bar'>
      <div className='pagination-space'></div>
      <div className='pagination-text'>
        <BlockText>{generateDisplayRangeText(displayInfo)}</BlockText>
      </div>
      <div className='pagination-buttons'>
        <Button
          title='pagination button first'
          className={disableBack ? 'button-disabled': ''}
          onClick={firstHandler}
        >
          |&lt;
        </Button>&nbsp;&nbsp;
        <Button
          title='pagination button back'
          className={disableBack ? 'button-disabled': ''}
          onClick={backHandler}
        >
          &lt;
        </Button>&nbsp;&nbsp;&nbsp;&nbsp;
        <Button
          title='pagination button next'
          className={disableNext ? 'button-disabled' : ''}
          onClick={nextHandler}
        >
          &gt;
        </Button>&nbsp;&nbsp;
        <Button
          title='pagination button last'
          className={disableNext ? 'button-disabled' : ''}
          onClick={lastHandler}
        >
          &gt;|
        </Button>
      </div>
    </div>
  );
};

const generateDisplayRangeText = (displayInfo) => {
  const { firstItemIdx, lastItemIdx, totalCount } = displayInfo;

  return `Displaying ${firstItemIdx}-${lastItemIdx} of ${totalCount}`;
};

export default PaginationBar;
