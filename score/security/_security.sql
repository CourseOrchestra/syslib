CREATE GRAIN security VERSION '1.3';

-- *** TABLES ***
CREATE TABLE subjects(
  sid VARCHAR(200) NOT NULL,
  name VARCHAR(255),
  employeeId VARCHAR(30),
  CONSTRAINT pk_subjects PRIMARY KEY (sid)
);

CREATE TABLE logins(
  subjectId VARCHAR(200),
  userName VARCHAR(255) NOT NULL,
  password VARCHAR(200) NOT NULL,
  CONSTRAINT pk_logins PRIMARY KEY (userName)
);

CREATE TABLE customPermsTypes(
  name VARCHAR(60) NOT NULL,
  description VARCHAR(200),
  CONSTRAINT pk_customPermsTypes PRIMARY KEY (name)
);

CREATE TABLE customPerms(
  name VARCHAR(60) NOT NULL,
  description VARCHAR(200),
  type VARCHAR(60) NOT NULL,
  CONSTRAINT pk_customPerms PRIMARY KEY (name)
);

CREATE TABLE rolesCustomPerms(
  roleid VARCHAR(16) NOT NULL,
  permissionId VARCHAR(60) NOT NULL,
  CONSTRAINT pk_rolesCustomPerms PRIMARY KEY (roleid, permissionId)
);

-- *** FOREIGN KEYS ***
ALTER TABLE customPerms ADD CONSTRAINT fk_security_customPerm5E921445 FOREIGN KEY (type) REFERENCES security.customPermsTypes(name);
ALTER TABLE rolesCustomPerms ADD CONSTRAINT fk_security_rolesCusto0E151131 FOREIGN KEY (roleid) REFERENCES celesta.roles(id);
ALTER TABLE rolesCustomPerms ADD CONSTRAINT fk_security_rolesCusto4BC26BD1 FOREIGN KEY (permissionId) REFERENCES security.customPerms(name);
-- *** INDICES ***
-- *** VIEWS ***
CREATE VIEW tablesPermissionsView as
SELECT
	roles.id AS roleid,
	tables.grainid AS grainid,
	tables.tablename AS tablename,
	perm.r AS r,
	perm.i AS i,
	perm.m AS m,
	perm.d AS d
FROM
	celesta.roles AS roles
INNER JOIN celesta.tables AS tables ON 1=1
LEFT JOIN celesta.permissions AS perm ON roles.id = perm.roleid
AND tables.grainid = perm.grainid
AND tables.tablename = perm.tablename;