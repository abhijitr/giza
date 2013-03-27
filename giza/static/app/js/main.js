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
    },
    shim: {
        'backbone': {
            deps: ['underscore', 'json2'],
            exports: 'Backbone'
        },
    },
    hbs: {
        templateExtension : 'hbs',
        disableI18n: true
    },
});

requirejs(
    [
        'jquery',
        'backbone',
        'app/app',
    ],
    function($, Backbone, AppRouter) {
        window.GIZA = {};

        window.GIZA.router = new AppRouter();
        Backbone.history.start({pushState: true});
    }
);
