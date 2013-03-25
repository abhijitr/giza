define(
    [
        'jquery',
        'backbone',
    ],
    function($, Backbone) {
        // Set up routing
        var AppController = Backbone.Router.extend({
            routes: {},

            initialize: function() {
                var router = this;
                var routes = [
                    [/^$/, 'home', this.home],
                    [/about/, 'getAbout', this.about],
                ];
            
                _.each(routes, function(route) {
                    router.route.apply(router,route);
                });
            },

            home: function() {
                console.log('home!');
            },

            about: function() {
                console.log('about!');
            }
        });

        return AppController;
    }
);
