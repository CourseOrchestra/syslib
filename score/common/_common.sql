create grain common version '1.01';

create table numbersSeries (
id varchar(50) not null primary key,
description varchar(250)
);

create table linesOfNumbersSeries (
seriesId varchar(50) not null foreign key references numbersSeries(id),
numberOfLine int not null,
startingDate datetime not null,
startingNumber int  not null,
endingNumber int  not null,
incrimentByNumber int not null,
lastUsedNumber int,
prefix varchar(20) not null default '',
postfix varchar(20) not null default '',
isFixedLength bit not null default 'TRUE',
isOpened bit not null default 'TRUE',
lastUsedDate datetime,

PRIMARY KEY (seriesId, numberOfLine)
);

create table htmlHints (
elementId varchar(50) not null primary key,
htmlText varchar(20000),
showOnLoad int
);