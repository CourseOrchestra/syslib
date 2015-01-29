CREATE GRAIN security VERSION '1.2';

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
--ALTER TABLE subjects ADD CONSTRAINT fk_security_subjects_o9FCB0700 FOREIGN KEY (employeeId) REFERENCES orgstructure.employees(id) ON DELETE SET NULL;
--ALTER TABLE logins ADD CONSTRAINT fk_security_logins_sec001C7D9E FOREIGN KEY (subjectId) REFERENCES security.subjects(sid) ON DELETE CASCADE;
ALTER TABLE customPerms ADD CONSTRAINT fk_security_customPerm5E921445 FOREIGN KEY (type) REFERENCES security.customPermsTypes(name);
ALTER TABLE rolesCustomPerms ADD CONSTRAINT fk_security_rolesCusto0E151131 FOREIGN KEY (roleid) REFERENCES celesta.roles(id);
ALTER TABLE rolesCustomPerms ADD CONSTRAINT fk_security_rolesCusto4BC26BD1 FOREIGN KEY (permissionId) REFERENCES security.customPerms(name);
-- *** INDICES ***
-- *** VIEWS ***
