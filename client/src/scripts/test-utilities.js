// file to put all utility methods used in tests

// sets value on controlled component
// https://stackoverflow.com/questions/40894637/how-to-programmatically-fill-input-elements-built-with-react
export function setNativeValue(element, value) {
    const valueSetter = Object.getOwnPropertyDescriptor(element, 'value').set;
    const prototype = Object.getPrototypeOf(element);
    const prototypeValueSetter = Object.getOwnPropertyDescriptor(prototype, 'value').set;
  
    if (valueSetter && valueSetter !== prototypeValueSetter) {
        prototypeValueSetter.call(element, value);
    } else {
        valueSetter.call(element, value);
    }
}

export function createMockFetch(ok, status, jsonFunc) {
    const fetchImpl = createMockFetchImplementation(ok, status, jsonFunc);
    return jest.fn(fetchImpl).mockName('Mocked fetch()');
}

export function createMockFetchImplementation(ok, status, jsonFunc) {
    const response = Promise.resolve({ ok, status, json: jsonFunc });
    return () => response;
}

export function createErrorJsonData(msg) {
    return {
        error: {
            description: msg
        }
    };
}