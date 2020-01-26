import React from 'react';

import Post from '../post/post.component';

class Threads extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      posts: []
    };
  }

  componentDidMount() {
    console.log('Thread Component mounted!');
    fetch('https://jsonplaceholder.typicode.com/posts')
    .then(response => {
      return response.json();
    })
    .then(json => {
      this.setState({posts: json}, () => {
        console.log(this.state.posts);
      });
    })
    .catch(error => {
      console.log(error);
    })
  }

  render() {
    return (
      <div className='threads'>
        {
          this.state.posts.map(post => 
            <Post key={post.id} {...post} />
          )
        }
      </div>
    );
  }
}

export default Threads;