
/* calculates rmse for all players that we had in a lineup regardless of position (e.g. PG1/PG2/ and SG1/SG2) */
truncate rmse_mlpFloor_all_players;

insert into rmse_mlpFloor_all_players(playerID, playerName, avg_projPoints, avg_actualPoints, rmse)
select playerID, playerName, avg(projPoints), avg(actualPoints), SQRT(AVG(POWER(projPoints - actualPoints, 2))) as rmse from mlpFloor_players group by 1,2 order by 5;


/* use below for players table with projected points and actual points */
CREATE TABLE `mlpFloor_players` (
  `playerID` int(11) NOT NULL,
  `playerName` varchar(45) NOT NULL DEFAULT '',
  `projPoints` double DEFAULT NULL,
  `actualPoints` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

truncate mlpFloor_players;
truncate historic_mlpFloor_lineups;
insert into historic_mlpFloor_lineups
select distinct * from historic_lineups where model="mlpFloor1";

/* calculates all PG1 data and inserts into mlp_players table */
insert into mlpFloor_players(playerID, playerName, projPoints, actualPoints)
select PG1playerID as playerID, PG1 as playerName, projPointsPG1 as projPoints, actualPointsPG1 as actualPoints from historic_mlpFloor_lineups;

/* calculates all PG2 data and inserts into mlp_players table */
insert into mlpFloor_players(playerID, playerName, projPoints, actualPoints)
select PG2playerID as playerID, PG2 as playerName, projPointsPG2 as projPoints, actualPointsPG2 as actualPoints from historic_mlpFloor_lineups;


/* calculates all SG1 data and inserts into mlp_players table */
insert into mlpFloor_players(playerID, playerName, projPoints, actualPoints)
select SG1playerID as playerID, SG1 as playerName, projPointsSG1 as projPoints, actualPointsSG1 as actualPoints from historic_mlpFloor_lineups;


/* calculates all SG2 data and inserts into mlp_players table */
insert into mlpFloor_players(playerID, playerName, projPoints, actualPoints)
select SG2playerID as playerID, SG2 as playerName, projPointsSG2 as projPoints, actualPointsSG2 as actualPoints from historic_mlpFloor_lineups;


/* calculates all SF1 data and inserts into mlp_players table */
insert into mlpFloor_players(playerID, playerName, projPoints, actualPoints)
select SF1playerID as playerID, SF1 as playerName, projPointsSF1 as projPoints, actualPointsSF1 as actualPoints from historic_mlpFloor_lineups;

/* calculates all SF2 data and inserts into mlp_players table */
insert into mlpFloor_players(playerID, playerName, projPoints, actualPoints)
select SF2playerID as playerID, SF2 as playerName, projPointsSF2 as projPoints, actualPointsSF2 as actualPoints from historic_mlpFloor_lineups;

/* calculates all PF1 data and inserts into mlp_players table */
insert into mlpFloor_players(playerID, playerName, projPoints, actualPoints)
select PF1playerID as playerID, PF1 as playerName, projPointsPF1 as projPoints, actualPointsPF1 as actualPoints from historic_mlpFloor_lineups;

/* calculates all PF2 data and inserts into mlp_players table */
insert into mlpFloor_players(playerID, playerName, projPoints, actualPoints)
select PF2playerID as playerID, PF2 as playerName, projPointsPF2 as projPoints, actualPointsPF2 as actualPoints from historic_mlpFloor_lineups;

/* calculates all C data and inserts into mlp_players table */
insert into mlpFloor_players(playerID, playerName, projPoints, actualPoints)
select CplayerID as playerID, C as playerName, projPointsC as projPoints, actualPointsC as actualPoints from historic_mlpFloor_lineups;


drop table mlpFloor_players;
