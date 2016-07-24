-- Quick and dirty datamodel for the hackday
CREATE DATABASE travel_tracker;

USE travel_tracker;

CREATE TABLE instagram_photos(
	id int not null AUTO_INCREMENT,
	instagram_id varchar(40),
	link varchar(100),
	file_path varchar(100),
	text varchar(1000),
	latitude decimal(7, 5),
	longitude decimal(7, 5),
	created_time timestamp,
	primary key(id)
);
