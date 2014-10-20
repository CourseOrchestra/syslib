/**{
"1":"Папка1",
"1.1":"Папка1.1",
"1.2":"Папка1.2",
"1.2.1":"Папка1.2.1",
"1.3":"Папка1.3",
"2":"Папка2",
"3":"Папка3",
"3.1":"Папка3.1",
"3.2":"Папка3.2",
"3.2.1":"Папка3.2.1"
}*/
create grain testgrain version '1.0';

/**{"name":"Сотрудники","grainId":"dirusing","dbTableName":"testgrain.employees","folderId":"3.2.1","dirTypeId":"1"}*/
create table employees (
/**{"name":"id","fieldTypeId":"9","precision":"NULL","fieldOrderInGrid":"0","isRequired":"1","visualLength":"0","fieldOrderInSort":"0"}*/
id int IDENTITY not null, 
/**{"name":"Имя","fieldTypeId":"9","precision":"NULL","fieldOrderInGrid":"1","isRequired":"1","visualLength":"NULL","fieldOrderInSort":"1"}*/
name varchar(30) not null,
/**{"name":"Фамилия","fieldTypeId":"9","precision":"NULL","fieldOrderInGrid":"2","isRequired":"0","visualLength":"NULL","fieldOrderInSort":"2"}*/
lastname varchar(30) not null,
/**{"name":"Адрес","fieldTypeId":"7","precision":"NULL","fieldOrderInGrid":"30","refTable":"adresses_new","refTableColumn":"country","length":"30","isRequired":"0","visualLength":"NULL","fieldOrderInSort":"3"}*/
adress_id varchar(10) , 
/**{"name":"Адреса","fieldTypeId":"6","precision":"NULL","fieldOrderInGrid":"40","refTable":"adresses","refMappingTable":"mapping_test","refTableColumn":"flat","length":"30","precision":"NULL","isRequired":"0","visualLength":"NULL","fieldOrderInSort":"4"}*/
adress_ids varchar(4000) , 
primary key (id, name)
);

/**{"name":"Адреса","grainId":"dirusing","dbTableName":"testgrain.adresses","folderId":"2","dirTypeId":"1"}*/
create table adresses (
/**{"name":"Индекс","fieldTypeId":"9","precision":"NULL","fieldOrderInGrid":"1","isRequired":"1","visualLength":"NULL","fieldOrderInSort":"1"}*/
postalcode varchar(10) not null,
/**{"name":"Страна","fieldTypeId":"9","precision":"NULL","fieldOrderInGrid":"2","isRequired":"0","visualLength":"NULL","fieldOrderInSort":"2"}*/
country varchar(30) not null,
/**{"name":"Город","fieldTypeId":"9","precision":"NULL","fieldOrderInGrid":"3","isRequired":"0","visualLength":"NULL","fieldOrderInSort":"3"}*/
city varchar(30) not null,
/**{"name":"Улица","fieldTypeId":"9","precision":"NULL","fieldOrderInGrid":"4","isRequired":"0","visualLength":"NULL","fieldOrderInSort":"4"}*/
street varchar(50) not null,
/**{"name":"Дом","fieldTypeId":"9","precision":"NULL","fieldOrderInGrid":"5","isRequired":"1","visualLength":"NULL","fieldOrderInSort":"5"}*/
building varchar(5) not null,
/**{"name":"Квартира","fieldTypeId":"9","precision":"NULL","fieldOrderInGrid":"6","isRequired":"1","visualLength":"NULL","fieldOrderInSort":"6"}*/
flat varchar(5) not null,
/**{"name":"Файл","fieldTypeId":"4","precision":"NULL","fieldOrderInGrid":"7","isRequired":"0","visualLength":"NULL","fieldOrderInSort":7"}*/
attachment blob,
primary key (postalcode, building, flat)
);

/**{"name":"Адреса-2","grainId":"dirusing","dbTableName":"testgrain.adresses_new","folderId":"","dirTypeId":"1"}*/
create table adresses_new (
/**{"name":"Индекс","fieldTypeId":"9","precision":"NULL","fieldOrderInGrid":"1","isRequired":"1","visualLength":"NULL","fieldOrderInSort":"1"}*/
postalcode varchar(10) not null,
/**{"name":"Страна","fieldTypeId":"9","precision":"NULL","fieldOrderInGrid":"2","isRequired":"0","visualLength":"NULL","fieldOrderInSort":"2"}*/
country varchar(30) not null,
/**{"name":"Город","fieldTypeId":"9","precision":"NULL","fieldOrderInGrid":"3","isRequired":"0","visualLength":"NULL","fieldOrderInSort":"3"}*/
city varchar(30) not null,
/**{"name":"Улица","fieldTypeId":"9","precision":"NULL","fieldOrderInGrid":"4","isRequired":"0","visualLength":"NULL","fieldOrderInSort":"4"}*/
street varchar(50) not null,
/**{"name":"Дом","fieldTypeId":"9","precision":"NULL","fieldOrderInGrid":"5","isRequired":"1","visualLength":"NULL","fieldOrderInSort":"5"}*/
building varchar(5) not null,
/**{"name":"Квартира","fieldTypeId":"9","precision":"NULL","fieldOrderInGrid":"6","isRequired":"1","visualLength":"NULL","fieldOrderInSort":"6"}*/
flat varchar(5) not null,
/**{"name":"Файл","fieldTypeId":"4","precision":"NULL","fieldOrderInGrid":"7","isRequired":"0","visualLength":"NULL","fieldOrderInSort":"7"}*/
attachment blob,
primary key (postalcode)
);


create table mapping_test (
id int IDENTITY not null, 
ak1 int not null,
ak2 varchar(30) not null,
bk1 varchar(10) not null,
bk2 varchar(5) not null,
bk3 varchar(5) not null,
primary key (id)
);

ALTER TABLE mapping_test ADD CONSTRAINT FK_mapping_test_adresses
FOREIGN KEY (bk1, bk2, bk3) REFERENCES adresses(postalcode, building, flat);

ALTER TABLE mapping_test ADD CONSTRAINT FK_mapping_test_employees
FOREIGN KEY (ak1,ak2) REFERENCES employees(id,name);