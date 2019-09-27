create view players as
select playerID, nickName from player_reference;

create view players_performance as
select players.nickName as playerName, performance.* from players left join performance on players.playerID = performance.playerID;

truncate player_stats;
insert into player_stats(playerName, playerID, dateID, blocks, points, steals, assists, turnovers, totalRebounds, tripleDouble, doubleDouble, fanduel, draftkings, 3PM, offensiveRebounds, defensiveRebounds, 
minutesPlayed, fieldGoals, fieldGoalsAttempted, fieldGoalPercent, 3PA, 3PPercent, FT, FTA, FTPercent, personalFouls, plusMinus, trueShootingPercent, effectiveFieldGoalPercent, 3pointAttemptRate, freeThrowAttemptRate, offensiveReboundPercent, defensiveReboundPercent, totalReboundPercent, assistPercent, stealPercent, blockPercent, turnoverPercent, usagePercent, offensiveRating, defensiveRating, team, opponent, home, fanduelPosition, draftkingsPosition, fanduelPts, draftkingsPts)
select playerName, playerID, dateID, blocks, points, steals, assists, turnovers, totalRebounds, tripleDouble, doubleDouble, fanduel, draftkings, 3PM, offensiveRebounds, defensiveRebounds, 
minutesPlayed, fieldGoals, fieldGoalsAttempted, fieldGoalPercent, 3PA, 3PPercent, FT, FTA, FTPercent, personalFouls, plusMinus, trueShootingPercent, effectiveFieldGoalPercent, 3pointAttemptRate, freeThrowAttemptRate, offensiveReboundPercent, defensiveReboundPercent, totalReboundPercent, assistPercent, stealPercent, blockPercent, turnoverPercent, usagePercent, offensiveRating, defensiveRating, team, opponent, home, fanduelPosition, draftkingsPosition, fanduelPts, draftkingsPts from players_performance;

drop view players;
drop view players_performance;

drop table player_stats;
CREATE TABLE `player_stats` (
  `playerName` varchar(45) NOT NULL DEFAULT '',
  `playerID` int(11) DEFAULT NULL,
  `dateID` int(11) DEFAULT NULL,
  `blocks` int(11) DEFAULT NULL,
  `points` int(11) DEFAULT NULL,
  `steals` int(11) DEFAULT NULL,
  `assists` int(11) DEFAULT NULL,
  `turnovers` int(11) DEFAULT NULL,
  `totalRebounds` int(11) DEFAULT NULL,
  `tripleDouble` int(11) DEFAULT NULL,
  `doubleDouble` int(11) DEFAULT NULL,
  `fanduel` int(11) DEFAULT NULL,
  `draftkings` int(11) DEFAULT NULL,
  `3PM` int(11) DEFAULT NULL,
  `offensiveRebounds` int(11) DEFAULT NULL,
  `defensiveRebounds` float DEFAULT NULL,
  `minutesPlayed` float DEFAULT NULL,
  `fieldGoals` int(11) DEFAULT NULL,
  `fieldGoalsAttempted` int(11) DEFAULT NULL,
  `fieldGoalPercent` float DEFAULT NULL,
  `3PA` int(11) DEFAULT NULL,
  `3PPercent` float DEFAULT NULL,
  `FT` int(11) DEFAULT NULL,
  `FTA` int(11) DEFAULT NULL,
  `FTPercent` float DEFAULT NULL,
  `personalFouls` int(11) DEFAULT NULL,
  `plusMinus` int(11) DEFAULT NULL,
  `trueShootingPercent` float DEFAULT NULL,
  `effectiveFieldGoalPercent` float DEFAULT NULL,
  `3pointAttemptRate` float DEFAULT NULL,
  `freeThrowAttemptRate` float DEFAULT NULL,
  `offensiveReboundPercent` float DEFAULT NULL,
  `defensiveReboundPercent` float DEFAULT NULL,
  `totalReboundPercent` float DEFAULT NULL,
  `assistPercent` float DEFAULT NULL,
  `stealPercent` float DEFAULT NULL,
  `blockPercent` float DEFAULT NULL,
  `turnoverPercent` float DEFAULT NULL,
  `usagePercent` float DEFAULT NULL,
  `offensiveRating` int(11) DEFAULT NULL,
  `defensiveRating` int(11) DEFAULT NULL,
  `team` varchar(45) DEFAULT NULL,
  `opponent` varchar(45) DEFAULT NULL,
  `home` int(11) DEFAULT NULL,
  `fanduelPosition` varchar(45) DEFAULT NULL,
  `draftkingsPosition` varchar(45) DEFAULT NULL,
  `fanduelPts` float DEFAULT '0',
  `draftkingsPts` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;