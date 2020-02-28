import React from 'react';
import { render, screen, cleanup } from '@testing-library/react';

import BasePage from '../pages/base/base-page.component';

afterEach(cleanup);

function renderBasePage() {
    return render(<div id='root'><BasePage /></div>);
}

describe('Testing BasePage', () => {
    test('Clicking on login should blur the page', () => {
        const { container, getByText } = renderBasePage();
        const login = getByText('LOGIN');
        const getBasePageClasses = () => {
            return container.firstChild.firstChild.getAttribute('Class').split(' ');
        }

        const beforeClasses = getBasePageClasses();
        expect(beforeClasses).not.toContain('blurred');

        login.click();

        const afterClasses = getBasePageClasses();
        expect(afterClasses).toContain('blurred');
    });

    test('Clicking on login should bring up modal', () => {
        const { container, getByText } = renderBasePage();
        const login = getByText('LOGIN');

        expect( screen.queryByTitle('modal-login') ).toBeNull();

        login.click();

        expect( screen.queryByTitle('modal-login') ).not.toBeNull();
    });
});