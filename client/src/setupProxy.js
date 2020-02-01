const proxy = require('http-proxy-middleware');

module.exports = (app) => {
    app.use( proxy('/v1', { target: 'http://localhost:5000' }) );
    app.use( proxy(['/userlist', '/postlist'], { target: 'http://localhost:5000' }) );
};