import React from 'react';
import { Link } from 'react-router-dom';

import './breadcrumbs.styles.scss';

const Breadcrumbs = ({ links }) => {
  return (
    <div className='breadcrumbs'>
      { createLinkComponentsFromProp(links) }
    </div>
  );
};

function createLinkComponentsFromProp(links) {
  const components = links
    .map(link => createComponentFromLinkProp(link))
    // insert a separator element between each link
    .reduce((acc, curr, idx) => acc.concat(curr, createSeparator(idx)), [])
    // ignore the final separator
    .slice(0, -1);

  return components;
}

// replace Link component with a <p> when path is null
function createComponentFromLinkProp(link) {
  const { displayName, path, state } = link;
  if (!path)
    return (
      <p
        key={ displayName }
        className='breadcrumbs-inactive-link'
      >
        { displayName }
      </p>
    );
  else
    return (
      <Link
        key={ displayName }
        className='breadcrumbs-active-link'
        to={{
          pathname: path,
          state: state
        }}
      >
        { displayName }
      </Link>
    );
}

function createSeparator(idx) {
  return <p className='breadcrumbs-separator' key={idx}>/</p>;
}

export default Breadcrumbs;
