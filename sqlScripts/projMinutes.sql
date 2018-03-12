UPDATE performance as p
SET projMinutes = (
	SELECT minutes FROM player_seven_daily_avg as d
    WHERE p.dateID = d.dateID AND p.playerID = d.playerID)
WHERE p.projMinutes IS NULL