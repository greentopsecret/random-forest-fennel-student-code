Feature: stateless mock server

Scenario: pathMatches('/s-fahrraeder/berlin/preis:300:/seite:1/fahrrad/k0c217l3331')
    * def response = read('output/ebay-fahrrad-page-1.html')

Scenario: pathMatches('/s-fahrraeder/berlin/preis:300:/seite:2/fahrrad/k0c217l3331')
    * def response = read('output/ebay-fahrrad-page-2.html')

Scenario: pathMatches('/s-fahrraeder/berlin/preis:300:/seite:3/fahrrad/k0c217l3331')
    * def response = read('output/ebay-fahrrad-page-3.html')

Scenario: pathMatches('/s-fahrraeder/anzeige:angebote/seite:1/fahrrad/k0c217')
    * def response = read('output/ebay-fahrrad-page-1.html')

Scenario: pathMatches('/s-fahrraeder/anzeige:angebote/seite:2/fahrrad/k0c217')
    * def response = read('output/ebay-fahrrad-page-2.html')

Scenario: pathMatches('/s-fahrraeder/anzeige:angebote/seite:3/fahrrad/k0c217')
    * def response = read('output/ebay-fahrrad-page-3.html')