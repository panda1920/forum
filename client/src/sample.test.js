function sum(a, b) {
    return a + b;
}

test('sum() function should return 5 when 2 and 3 are passed', () => {
    expect(sum(2, 3)).toBe(5);
});