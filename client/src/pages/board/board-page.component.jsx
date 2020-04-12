import React, { useEffect, useContext, useState } from 'react';

import ThreadCard from '../../components/thread-card/thread-card.component';

import { searchThreads } from '../../scripts/api';
import { CurrentUserContext } from '../../contexts/current-user/current-user';

import './board-page.styles.scss';

const BoardPage = ({ boardId }) => {
  const { setCurrentUser } = useContext(CurrentUserContext);
  const [ threads, setThreads ] = useState([]);

  useEffect(() => {
    let getThreadsInformation = async () => {
      const response =  await searchThreads({ boardId });
      if (!response.ok)
        return;
      
      const { result, sessionUser } = await response.json();
      setThreads(result.threads);
      setCurrentUser(sessionUser);
    };

    getThreadsInformation();
  }, [ boardId, setCurrentUser ]);

  return (
    <div className='board-page' title='board page'>
      <div title='navigation bar'>HOME &gt;&gt; PLACEHOLDER</div>
      <h1 title='page heading'>PLACEHOLDER BOARD HEADING</h1>
      <div title='board info'>
        Some placeholder board title<br/>
        Created by placeholder_user at 1/1/2020 12:00:00
      </div>
      <div title='pagination bar'>|&lt;  &lt;  &gt;  &gt;|</div>
      <div title='threads list'>
        {
          threads.map(thread => <ThreadCard key={thread.threadId} threadInfo={thread} />)
        }
      </div>
      <div title='pagination bar'>|&lt;  &lt;  &gt;  &gt;|</div>
      <div title='navigation bar'>HOME &gt;&gt; PLACEHOLDER</div>
    </div>
  );
};

export default BoardPage;