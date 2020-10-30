import React, { useEffect, useContext, useState } from 'react';

import Button from '../../components/button/button.component';
import BlockText from '../../components/block-text/block-text.component';
import ThreadList from '../../components/thread-list/thread-list.component';

import { CurrentUserContext } from '../../contexts/current-user/current-user';

import './board-page.styles.scss';

const PAGE_SIZE = 5;

const BoardPage = ({ boardId }) => {
  return (
    <div className='board-page' title='board page'>
      <div title='navigation bar'>HOME &gt;&gt; PLACEHOLDER</div>
      <h1 title='page heading'>PLACEHOLDER BOARD HEADING</h1>
      <div title='board info'>
        Some placeholder board title<br/>
        Created by placeholder_user at 1/1/2020 12:00:00
      </div>
      <ThreadList boardId={boardId} pageSize={PAGE_SIZE} />
      <div title='navigation bar'>HOME &gt;&gt; PLACEHOLDER</div>
    </div>
  );
};

export default BoardPage;