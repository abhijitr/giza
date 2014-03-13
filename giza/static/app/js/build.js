({
    baseUrl: "../../vendor/js",     /* make it so paths are all relative to almond.js */
    optimize: 'none',               /* webassets filter will take care of optimization */
    mainConfigFile: 'main.js',      /* this one guy has to be relative to the build file :P */
    name: 'almond',                 /* use almond.js as the main entry point */
    include: [
        'app/main'
    ],
})
