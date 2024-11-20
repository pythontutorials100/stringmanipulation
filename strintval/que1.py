PREFIX : <http://api.stardog.com/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?ibe_part_number ?ice_part_number ?part ?partQuality ?qualityName ?partValue
       ?icePartQuality ?ibePartQuality
       ?specification ?specQualitySpec ?qualityNameSpec ?specValue
       ?ibeSpecQuality
       ?process ?ice_process ?ibe_process ?processDescription
WHERE {
  # Retrieve the Part Number and Part Item
  ?ibe_part_number a :Information_Bearing_Entity ;
                   :has_text_value "PN-1025"^^xsd:string .
  ?ice_part_number a :Part_Number ;
                   :generically_depends_on ?ibe_part_number ;
                   :designates ?part .

  # Retrieve the Part's Qualities and Values
  ?part :bearer_of ?partQuality .
  ?icePartQuality :describes ?partQuality ;
                  :generically_depends_on ?ibePartQuality .
  ?ibePartQuality :has_boolean_value ?partValue .

  # Extract the quality name
  BIND(STRAFTER(STR(?partQuality), "http://api.stardog.com/") AS ?fullPartQualityName)
  BIND(REPLACE(?fullPartQualityName, "^(.*)_\\d+\\.\\d+$", "$1") AS ?qualityName)

  # Retrieve Specifications and their Qualities
  ?specification a :Directive_Information_Content_Entity ;
                 :has_part ?specQualitySpec ;
                 :is_about ?plan .
  ?plan :prescribes ?process .
  ?ice_process a :Designative_Information_Content_Entity ;
               :designates ?process ;
               :generically_depends_on ?ibe_process .
  ?ibe_process a :Information_Bearing_Entity ;
               :has_text_value ?processDescription .
  ?specQualitySpec :generically_depends_on ?ibeSpecQuality .
  ?ibeSpecQuality :has_boolean_value ?specValue .

  # Extract the specification quality name
  BIND(STRAFTER(STR(?specQualitySpec), "http://api.stardog.com/") AS ?fullSpecQualityName)
  BIND(REPLACE(?fullSpecQualityName, "^(ice_)?(.*)_spec_\\d+\\.\\d+$", "$2") AS ?qualityNameSpec)

  # Compare Qualities and Values
  FILTER(?qualityName = ?qualityNameSpec)
  FILTER(?partValue = ?specValue)

  # Exclude specifications where there is a quality requirement not matched by the part
  FILTER NOT EXISTS {
    ?specification :has_part ?specQualitySpec2 .
    ?specQualitySpec2 :generically_depends_on ?ibeSpecQuality2 .
    ?ibeSpecQuality2 :has_boolean_value ?specValue2 .
    BIND(STRAFTER(STR(?specQualitySpec2), "http://api.stardog.com/") AS ?fullSpecQualityName2)
    BIND(REPLACE(?fullSpecQualityName2, "^(ice_)?(.*)_spec_\\d+\\.\\d+$", "$2") AS ?qualityNameSpec2)

    # Check if the part lacks this quality or the values don't match
    FILTER NOT EXISTS {
      ?part :bearer_of ?partQuality2 .
      ?icePartQuality2 :describes ?partQuality2 ;
                       :generically_depends_on ?ibePartQuality2 .
      ?ibePartQuality2 :has_boolean_value ?partValue2 .
      BIND(STRAFTER(STR(?partQuality2), "http://api.stardog.com/") AS ?fullPartQualityName2)
      BIND(REPLACE(?fullPartQualityName2, "^(.*)_\\d+\\.\\d+$", "$1") AS ?qualityName2)
      FILTER(?qualityName2 = ?qualityNameSpec2)
      FILTER(?partValue2 = ?specValue2)
    }
  }
}
ORDER BY ?specification ?qualityName
