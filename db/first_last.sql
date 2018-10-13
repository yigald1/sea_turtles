SELECT TurtleEvent.EventTurtleID, Turtle.TurtleName, Turtle.SpecieId, Turtle.TurtleGender, Specie.SpecieNameEng, First(TurtleEvent.EventDate) AS first_event_date, First(AcWeighing.Weight) AS first_weight, First(AcWeighing.[CCL-a]) AS first_CCL_a, First(AcWeighing.[CCW]) AS first_CCW, First(AcWeighing.[SCL-a]) AS first_SCL_a, First(AcWeighing.[SCW]) AS first_SCW, Last(AcWeighing.EventID) AS last_EventID, Last(TurtleEvent.EventDate) AS last_event_date, Last(AcWeighing.Weight) AS last_weight, Last(AcWeighing.[CCL-a]) AS last_CCL_a, Last(AcWeighing.[CCW]) AS last_CCW, Last(AcWeighing.[SCL-a]) AS last_SCL_a, Last(AcWeighing.[SCW]) AS last_SCW
FROM ((AcWeighing 
LEFT JOIN TurtleEvent ON AcWeighing.EventID = TurtleEvent.EventID) 
LEFT JOIN Turtle ON TurtleEvent.EventTurtleID = Turtle.TurtleId)
left join Specie on (Turtle.SpecieId = Specie.SpecieId)
WHERE TurtleEvent.EventActivityID=5
GROUP BY TurtleEvent.EventTurtleID, Turtle.TurtleName, Turtle.SpecieId, Turtle.TurtleGender, Specie.SpecieNameEng;

