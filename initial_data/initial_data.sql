insert or ignore into stats
(id, numofpositions, numofsubmissionslast24h)
values
(0, 0, 0);

insert or ignore into tags
(tag, donetagging, createdat)
values
('backgame', 1, current_timestamp),
('backgameopp', 1, current_timestamp),
('bearoff', 1, current_timestamp),
('closing', 1, current_timestamp),
('holding', 1, current_timestamp),
('holdingopp', 1, current_timestamp),
('midgame', 1, current_timestamp),
('nocontact', 1, current_timestamp),
('opening', 1, current_timestamp);
