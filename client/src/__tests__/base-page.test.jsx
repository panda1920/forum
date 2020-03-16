import React from 'react';
import { render, screen, cleanup } from '@testing-library/react';

import BasePage from '../pages/base/base-page.component';
import { ModalLoginTitle } from '../components/modal-login/modal-login.component';
import { ModalSignupTitle } from '../components/modal-signup/modal-signup.component';
import { act } from 'react-dom/test-utils';

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

        act(() => {
          login.click();
        });

        const afterClasses = getBasePageClasses();
        expect(afterClasses).toContain('blurred');
    });

    test('Clicking on login should bring up modal', () => {
      const { getByText } = renderBasePage();
        const login = getByText('LOGIN');

        expect( screen.queryByTitle(ModalLoginTitle) ).toBeNull();

        act(() => {
          login.click();
        });

        expect( screen.queryByTitle(ModalLoginTitle) ).not.toBeNull();
    });

    test('Clicking on signup should blur the page', () => {
      const { container, getByText } = renderBasePage();
      const signup = getByText('SIGNUP');
      const getBasePageClasses = () => {
          return container.firstChild.firstChild.getAttribute('Class').split(' ');
      }

      const beforeClasses = getBasePageClasses();
      expect(beforeClasses).not.toContain('blurred');

      act(() => {
        signup.click();
      });

      const afterClasses = getBasePageClasses();
      expect(afterClasses).toContain('blurred');
    });

    test('Clicking on signup should bring up modal', () => {
      const { getByText } = renderBasePage();
      const signup = getByText('SIGNUP');

      expect( screen.queryByTitle(ModalSignupTitle) ).toBeNull();

      act(() => {
        signup.click();
      });

      expect( screen.queryByTitle(ModalSignupTitle) ).not.toBeNull();
    });
});