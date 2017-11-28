UPDATE performance
SET fanduelPosition = 'SG'
WHERE playerID = 1772;

SELECT DISTINCT p.playerID, r.nickName, p.fanduelPosition 
FROM basketball.performance p
INNER JOIN player_reference r 
ON r.playerID = p.playerID
WHERE p.fanduelPosition IS NULL;