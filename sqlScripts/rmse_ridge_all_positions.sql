select avg(projPointsLineup), avg(actualPointsLineup), SQRT(AVG(POWER(projPointsLineup - actualPointsLineup, 2))) as rmse from historic_lineups where model="ridge1";
select avg(projPointsLineup), avg(actualPointsLineup), SQRT(AVG(POWER(projPointsLineup - actualPointsLineup, 2))) as rmse from historic_lineups where model="mlp1";


select avg(projPointsPG1), avg(actualPointsPG1), SQRT(AVG(POWER(projPointsPG1 - actualPointsPG1, 2))) as rmse from historic_lineups where model="ridge1";
select avg(projPointsPG1), avg(actualPointsPG1), SQRT(AVG(POWER(projPointsPG1 - actualPointsPG1, 2))) as rmse from historic_lineups where model="mlp1";

select avg(projPointsPG2), avg(actualPointsPG2), SQRT(AVG(POWER(projPointsPG2 - actualPointsPG2, 2))) as rmse from historic_lineups where model="ridge1";
select avg(projPointsPG2), avg(actualPointsPG2), SQRT(AVG(POWER(projPointsPG2 - actualPointsPG2, 2))) as rmse from historic_lineups where model="mlp1";

select avg(projPointsSG1), avg(actualPointsSG1), SQRT(AVG(POWER(projPointsSG1 - actualPointsSG1, 2))) as rmse from historic_lineups where model="ridge1";
select avg(projPointsSG1), avg(actualPointsSG1), SQRT(AVG(POWER(projPointsSG1 - actualPointsSG1, 2))) as rmse from historic_lineups where model="mlp1";

select avg(projPointsSG2), avg(actualPointsSG2), SQRT(AVG(POWER(projPointsSG2 - actualPointsSG2, 2))) as rmse from historic_lineups where model="ridge1";
select avg(projPointsSG2), avg(actualPointsSG2), SQRT(AVG(POWER(projPointsSG2 - actualPointsSG2, 2))) as rmse from historic_lineups where model="mlp1";

select avg(projPointsSF1), avg(actualPointsSF1), SQRT(AVG(POWER(projPointsSF1 - actualPointsSF1, 2))) as rmse from historic_lineups where model="ridge1";
select avg(projPointsSF1), avg(actualPointsSF1), SQRT(AVG(POWER(projPointsSF1 - actualPointsSF1, 2))) as rmse from historic_lineups where model="mlp1";

select avg(projPointsSF2), avg(actualPointsSF2), SQRT(AVG(POWER(projPointsSF2 - actualPointsSF2, 2))) as rmse from historic_lineups where model="ridge1";
select avg(projPointsSF2), avg(actualPointsSF2), SQRT(AVG(POWER(projPointsSF2 - actualPointsSF2, 2))) as rmse from historic_lineups where model="mlp1";

select avg(projPointsPF1), avg(actualPointsPF1), SQRT(AVG(POWER(projPointsPF1 - actualPointsPF1, 2))) as rmse from historic_lineups where model="ridge1";
select avg(projPointsPF1), avg(actualPointsPF1), SQRT(AVG(POWER(projPointsPF1 - actualPointsPF1, 2))) as rmse from historic_lineups where model="mlp1";

select avg(projPointsPF2), avg(actualPointsPF2), SQRT(AVG(POWER(projPointsPF2 - actualPointsPF2, 2))) as rmse from historic_lineups where model="ridge1";
select avg(projPointsPF2), avg(actualPointsPF2), SQRT(AVG(POWER(projPointsPF2 - actualPointsPF2, 2))) as rmse from historic_lineups where model="mlp1";

select avg(projPointsC), avg(actualPointsC), SQRT(AVG(POWER(projPointsC - actualPointsC, 2))) as rmse from historic_lineups where model="ridge1";
select avg(projPointsC), avg(actualPointsC), SQRT(AVG(POWER(projPointsC - actualPointsC, 2))) as rmse from historic_lineups where model="mlp1";

/* template for inserting into table */
truncate rmse_ridge_all_positions;

/* calculates all PG1 data and inserts into rmse_all_positions table */
insert into rmse_ridge_all_positions(playerID, playerName, lineupPosition, avg_projPoints, avg_actualPoints, rmse)
select PG1playerID, PG1, "PG1" as lineupPosition, avg(projPointsPG1), avg(actualPointsPG1), SQRT(AVG(POWER(projPointsPG1 - actualPointsPG1, 2))) as rmse from historic_lineups where model="ridge1" group by 1,2,3 order by 6;

/* calculates all PG2 data and inserts into rmse_all_positions table */
insert into rmse_ridge_all_positions(playerID, playerName, lineupPosition, avg_projPoints, avg_actualPoints, rmse)
select PG2playerID, PG2, "PG2" as lineupPosition, avg(projPointsPG2), avg(actualPointsPG2), SQRT(AVG(POWER(projPointsPG2 - actualPointsPG2, 2))) as rmse from historic_lineups where model="ridge1" group by 1,2,3 order by 6;

/* calculates all SG1 data and inserts into rmse_all_positions table */
insert into rmse_ridge_all_positions(playerID, playerName, lineupPosition, avg_projPoints, avg_actualPoints, rmse)
select PG1playerID, PG1, "PG1" as lineupPosition, avg(projPointsPG1), avg(actualPointsPG1), SQRT(AVG(POWER(projPointsPG1 - actualPointsPG1, 2))) as rmse from historic_lineups where model="ridge1" group by 1,2,3 order by 6;

/* calculates all SG2 data and inserts into rmse_all_positions table */
insert into rmse_ridge_all_positions(playerID, playerName, lineupPosition, avg_projPoints, avg_actualPoints, rmse)
select PG2playerID, PG2, "PG2" as lineupPosition, avg(projPointsPG2), avg(actualPointsPG2), SQRT(AVG(POWER(projPointsPG2 - actualPointsPG2, 2))) as rmse from historic_lineups where model="ridge1" group by 1,2,3 order by 6;

