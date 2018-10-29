select weight_change, days, weight_change / days as [weight_change_rate(gr/day)]
from (
select min(TurtleEvent.EventDate), min(AcWeighing.Weight), max(TurtleEvent.EventDate), max(AcWeighing.Weight), max(TurtleEvent.EventDate) - min(TurtleEvent.EventDate) as days, max(AcWeighing.Weight) - min(AcWeighing.Weight) as weight_change
 
from (


SELECT  TurtleEvent.EventTurtleId, Turtle.TurtleName, TurtleEvent.EventID, TurtleEvent.EventDate, AcWeighing.Weight, AcWeighing.[ccl-a], AcWeighing.ccw, AcWeighing.[scl-a], AcWeighing.scw
FROM (TurtleEvent 
LEFT JOIN Turtle ON TurtleEvent.EventTurtleID = Turtle.TurtleId)
LEFT JOIN AcWeighing ON TurtleEvent.EventID = AcWeighing.EventID
WHERE (((TurtleEvent.[EventActivityID])=5) AND ((TurtleEvent.[EventTurtleId])=7058))
ORDER BY TurtleEvent.EventDate));

