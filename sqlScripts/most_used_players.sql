
/* template for inserting into table */
truncate most_used_players;

insert into most_used_players(playerName, lineupPosition, count)
select PG1, "PG1" as lineupPosition, count(*) from historic_ridge1_lineups group by 1 order by 3 desc;

insert into most_used_players(playerName, lineupPosition, count)
select PG2, "PG2" as lineupPosition, count(*) from historic_ridge1_lineups group by 1 order by 3 desc;

insert into most_used_players(playerName, lineupPosition, count)
select SG1, "SG1" as lineupPosition, count(*) from historic_ridge1_lineups group by 1 order by 3 desc;

insert into most_used_players(playerName, lineupPosition, count)
select SG2, "SG2" as lineupPosition, count(*) from historic_ridge1_lineups group by 1 order by 3 desc;

insert into most_used_players(playerName, lineupPosition, count)
select SF1, "SF1" as lineupPosition, count(*) from historic_ridge1_lineups group by 1 order by 3 desc;

insert into most_used_players(playerName, lineupPosition, count)
select SF2, "SF2" as lineupPosition, count(*) from historic_ridge1_lineups group by 1 order by 3 desc;

insert into most_used_players(playerName, lineupPosition, count)
select PF1, "PF1" as lineupPosition, count(*) from historic_ridge1_lineups group by 1 order by 3 desc;

insert into most_used_players(playerName, lineupPosition, count)
select PF2, "PF2" as lineupPosition, count(*) from historic_ridge1_lineups group by 1 order by 3 desc;

insert into most_used_players(playerName, lineupPosition, count)
select C, "C" as lineupPosition, count(*) from historic_ridge1_lineups group by 1 order by 3 desc;

select * from most_used_players order by 3 desc;