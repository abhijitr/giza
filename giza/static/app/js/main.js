// usage: log('inside coolFunc', this, arguments);
// paulirish.com/2009/log-a-lightweight-wrapper-for-consolelog/
window.log = function f(){ log.history = log.history || []; log.history.push(arguments); if(this.console) { var args = arguments, newarr; args.callee = args.callee.caller; newarr = [].slice.call(args); if (typeof console.log === 'object') log.apply.call(console.log, console, newarr); else console.log.apply(console, newarr);}};

// make it safe to use console.log always
(function(a){function b(){}for(var c="assert,count,debug,dir,dirxml,error,exception,group,groupCollapsed,groupEnd,info,log,markTimeline,profile,profileEnd,time,timeEnd,trace,warn".split(","),d;!!(d=c.pop());){a[d]=a[d]||b;}})
(function(){try{console.log();return window.console;}catch(a){return (window.console={});}}());

requirejs.config({
    baseUrl: "/static/vendor/js",
    paths: {
        'app': '../../app/js',
        'jquery': 'jquery-1.9.0',
        'jquery-migrate': 'jquery-migrate-1.1.1'
    },
    shim: {
        'backbone': {
            deps: ['underscore', 'json2', 'jquery-migrate'],
            exports: 'Backbone'
        },
        'jquery.easing': ['jquery'],
    },
    hbs: {
        templateExtension : 'hbs',
        disableI18n: true
    },
});

requirejs([
    'jquery',
    'backbone',
],
function($, Backbone) {

    // Set up global singletons
    if (!window.APP) {
        window.APP = {};
    }

    // logged-in user
    //window.APP.user = new User(window.APP_OPTIONS.USER_DATA);

    var cmd = window.APP_OPTIONS.COMMAND;
    var args = window.APP_OPTIONS.COMMAND_ARGS || [];

});