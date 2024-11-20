CONSTRUCT {
  ?subject ?predicate ?object .
}
WHERE {
  ?subject ?predicate ?object .
  FILTER (?subject != owl:Class && ?object != owl:Class && ?subject != owl:Thing && ?object != owl:Thing)
}
