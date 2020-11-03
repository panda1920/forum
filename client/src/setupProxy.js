const proxy = require('http-proxy-middleware');

module.exports = (app) => {
    app.use( proxy('/api', {
        target: 'http://localhost:5000/v1',
        changeOrigin: true,
        pathRewrite: {
            '^/api': ''
        },
    }) );
    app.use( proxy(['/userlist', '/postlist'], {
        target: 'http://localhost:5000/v1',
        changeOrigin: true,
    }) );
};
