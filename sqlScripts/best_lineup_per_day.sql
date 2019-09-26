
create view proj_actual as
SELECT dateID, date, projPointsLineup, actualPointsLineup, model FROM basketball.historic_lineups;


create view max_actual as 
select dateID, date, max(actualPointsLineup) as actualPointsLineup from proj_actual group by 1,2 order by 1;


truncate `basketball`.`best_lineups`;
insert into best_lineups(dateID, date, projPointsLineup, actualPointsLineup, model)
select distinct max_actual.dateID, max_actual.date, proj_actual.projPointsLineup, max_actual.actualPointsLineup, proj_actual.model 
from max_actual left join proj_actual
on max_actual.dateID = proj_actual.dateID and max_actual.date = proj_actual.date 
and max_actual.actualPointsLineup = proj_actual.actualPointsLineup
order by 1;

drop view proj_actual;
drop view max_actual;