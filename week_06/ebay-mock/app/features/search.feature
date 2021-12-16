Feature: stateless mock server

Scenario: pathMatches('/s-wohnung-mieten/berlin/anzeige:angebote/seite:1/c203l3331+wohnung_mieten.qm_d:35,')
    * def response = read('output/ebay-wohnung-mieten-page-1.html')

Scenario: pathMatches('/s-wohnung-mieten/berlin/anzeige:angebote/seite:2/c203l3331+wohnung_mieten.qm_d:35,')
    * def response = read('output/ebay-wohnung-mieten-page-2.html')

Scenario: pathMatches('/s-wohnung-mieten/berlin/anzeige:angebote/seite:3/c203l3331+wohnung_mieten.qm_d:35,')
    * def response = read('output/ebay-wohnung-mieten-page-3.html')