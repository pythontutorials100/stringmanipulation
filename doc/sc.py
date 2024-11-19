INSERT DATA {
  GRAPH <tag:stardog:api:context:schema> {
      
#################################################################
#    Classes
#################################################################

:Descriptive_Information_Content_Entity rdf:type owl:Class .

:Designative_Information_Content_Entity rdf:type owl:Class .

:Directive_Information_Content_Entity rdf:type owl:Class .

:Information_Bearing_Entity rdf:type owl:Class .

:Part_Number rdf:type owl:Class .

:Part_item rdf:type owl:Class .

:Plan rdf:type owl:Class .

:Process rdf:type owl:Class .

:Quality rdf:type owl:Class .

:Quality_Specification rdf:type owl:Class .

#################################################################
#    Object Properties
#################################################################

:bearer_of rdf:type owl:ObjectProperty .

:describes rdf:type owl:ObjectProperty .

:designates rdf:type owl:ObjectProperty .

:generically_depends_on rdf:type owl:ObjectProperty .

:has_part rdf:type owl:ObjectProperty .

:is_about rdf:type owl:ObjectProperty .

:prescribes rdf:type owl:ObjectProperty .

#################################################################
#    Data Properties
#################################################################

:has_boolean_value rdf:type owl:DatatypeProperty .

:has_text_value rdf:type owl:DatatypeProperty .

#################################################################
#    Property Domain and Range Definitions
#################################################################

:has_text_value rdfs:range xsd:string .

:has_boolean_value rdfs:range xsd:boolean .


  }
}
