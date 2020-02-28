import React from 'react';
import { render, screen, cleanup } from '@testing-library/react';

import Header from '../components/header/header.component';

afterEach(cleanup);

describe('Tests for Header component', () => {
    test('sub-components should be rendered on screen', () => {
        const { container } = render(<Header />);

        const logo = screen.getByText('MYFORUMAPP');
        const signup = screen.getByText('SIGNUP');
        const login = screen.getByText('LOGIN');
    });
});