PREFIX : <http://api.stardog.com/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT ?partNumber ?specification ?processDescription
WHERE {
  # Retrieve the Part Number and Part Item
  ?ibe_part_number a :Information_Bearing_Entity ;
                   :has_text_value ?partNumber .
  FILTER(?partNumber = "PN-1025"^^xsd:string)
  ?ice_part_number a :Part_Number ;
                   :generically_depends_on ?ibe_part_number ;
                   :designates ?part .

  # Retrieve the Part's Qualities and Values
  ?part :bearer_of ?partQuality .
  ?icePartQuality :describes ?partQuality ;
                  :generically_depends_on ?ibePartQuality .
  ?ibePartQuality :has_boolean_value ?partValue .
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
  BIND(STRAFTER(STR(?specQualitySpec), "http://api.stardog.com/") AS ?fullSpecQualityName)
  BIND(REPLACE(?fullSpecQualityName, "^(ice_)?(.*)_spec_\\d+\\.\\d+$", "$2") AS ?qualityNameSpec)

  # Compare Qualities and Values
  FILTER(?qualityName = ?qualityNameSpec)
  BIND(IF(?partValue = ?specValue, 1, 0) AS ?match)
}
GROUP BY ?partNumber ?specification ?processDescription
HAVING (SUM(?match) = COUNT(DISTINCT ?specQualitySpec))
