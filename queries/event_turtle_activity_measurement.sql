SELECT Turtle.TurtleId, Turtle.TurtleName, TurtleEvent.EventDate, Activities.ActivityName, AcWeighing.Weight, [AcWeighing.CCL-a] AS Expr1, Count(TurtleEvent.EventID) AS activities
FROM ((TurtleEvent LEFT JOIN Turtle ON TurtleEvent.EventTurtleID = Turtle.TurtleId) LEFT JOIN Activities ON TurtleEvent.EventActivityID = Activities.ActivityID) LEFT JOIN AcWeighing ON TurtleEvent.EventTurtleID = AcWeighing.EventID
WHERE (((Turtle.TurtleId)=7058))
GROUP BY Turtle.TurtleId, Turtle.TurtleName, TurtleEvent.EventDate, Activities.ActivityName, AcWeighing.Weight, [AcWeighing.CCL-a]
ORDER BY Turtle.TurtleId DESC , Turtle.TurtleName, TurtleEvent.EventDate DESC , Activities.ActivityName, AcWeighing.Weight, [AcWeighing.CCL-a];