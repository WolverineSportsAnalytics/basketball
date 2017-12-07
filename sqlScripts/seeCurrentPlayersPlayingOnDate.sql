SELECT b.nickName, p.playerID, p.dateID, p.fanduel, p.minutesPlayed,
p.team, p.opponent, p.fanduelPosition, p.fanduelPts, p.fdPointsSKLinPredRidge, p.projMinutes
FROM basketball.performance as p
INNER JOIN basketball.player_reference as b ON b.playerID = p.playerID
WHERE p.dateID = 929;