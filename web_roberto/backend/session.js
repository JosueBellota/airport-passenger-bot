const session = require("express-session");

const sessionMiddleware = session({
    secret: "8f93k$2kS9@lQx!zP1mV#cD7wR",
    resave: false,
    saveUninitialized: false,
    cookie: {
        httpOnly: true,
        secure: false,
        maxAge: 1000 * 60 * 60
    }
});

module.exports = sessionMiddleware;