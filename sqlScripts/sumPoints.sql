update basketball.performance set draftkingsPts = (points + 3PM*.5 + totalRebounds*1.25 + steals*2 + blocks*2 -turnovers*.5 + doubleDouble + tripleDouble) where dateID = 1029;
update basketball.performance set fanduelPts = (FT + totalRebounds*1.2 + assists*1.5 + blocks*3 + steals*3 - turnovers + (3PM)*3 + (fieldGoals-3PM)*2) where dateID = 1029;


UPDATE basketball.futures as f, basketball.performance as p SET f.draftkingsPts = p.draftkingsPts, f.fanduelPts = p.fanduelPts WHERE f.dateID = p.dateID AND f.playerID = p.playerID AND f.dateID = 1029;

UPDATE basketball.futures as f
INNER JOIN basketball.performance as p ON (f.dateID = p.dateID AND f.playerID = p.playerID)
SET f.draftkingsPts = p.draftkingsPts, f.fanduelPts = p.fanduelPts
WHERE p.dateID = 1029;
