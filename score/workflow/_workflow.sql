CREATE GRAIN workflow VERSION '1.0';

-- *** TABLES ***
CREATE TABLE form(
  processKey varchar(30) NOT NULL,
  id INT NOT NULL,
  /**скрипт для открывания*/
  sOpen TEXT,
  /**скрипт для сохранения*/
  sSave TEXT,
  /**скрипт для действия*/
  sAction TEXT,
  link TEXT,
  isStartForm BIT NOT NULL DEFAULT 0,
  CONSTRAINT Pk_forms PRIMARY KEY (processKey,id)
);

CREATE TABLE status(
  id VARCHAR(50) NOT NULL,
  name VARCHAR(100) NOT NULL,
  modelId VARCHAR(50) NOT NULL,
  CONSTRAINT Pk_statuses PRIMARY KEY (id, modelId)
);

CREATE TABLE statusModel(
  id VARCHAR(50) NOT NULL,
  name VARCHAR(100) NOT NULL,
  CONSTRAINT Pk_statusModel PRIMARY KEY (id)
);

CREATE TABLE statusTransition(
  name VARCHAR(100) NOT NULL,
  statusFrom VARCHAR(50) NOT NULL,
  modelFrom VARCHAR(50) NOT NULL,
  statusTo VARCHAR(50) NOT NULL,
  modelTo VARCHAR(50) NOT NULL,
  CONSTRAINT PK_statusTransition PRIMARY KEY (statusFrom, modelFrom, statusTo, modelTo)
);

-- *** FOREIGN KEYS ***
ALTER TABLE status ADD CONSTRAINT fk_status FOREIGN KEY (modelId) REFERENCES workflow.statusModel(id);
ALTER TABLE statusTransition ADD CONSTRAINT fk_statustransition_status FOREIGN KEY (statusFrom, modelFrom) REFERENCES workflow.status(id, modelId);
ALTER TABLE statusTransition ADD CONSTRAINT fk_statustransition_status2 FOREIGN KEY (statusTo, modelTo) REFERENCES workflow.status(id, modelId);
-- *** INDICES ***
CREATE INDEX idx_statusTransition ON statusTransition(statusFrom, modelFrom);
CREATE INDEX idx_statusTransition_0 ON statusTransition(statusTo, modelTo);
-- *** VIEWS ***
