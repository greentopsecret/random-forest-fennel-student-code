function fn() {
    config = {};
    config.urlBase = 'http://web';
    // don't waste time waiting for a connection or if servers don't respond within 5 seconds
    karate.configure('connectTimeout', 500000);
    karate.configure('readTimeout', 500000);
    karate.configure('logPrettyRequest', true);
    karate.configure('logPrettyResponse', true);
    return config;
}
