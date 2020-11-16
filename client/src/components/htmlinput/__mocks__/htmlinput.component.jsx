import React from 'react';

const mockHtmlInput = () => {
  return <div />;
};

const HtmlInput = jest.fn()
  .mockName('Mocked Htmlnput')
  .mockImplementation(mockHtmlInput);

export default HtmlInput;
