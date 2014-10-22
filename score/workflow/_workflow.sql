CREATE GRAIN workflow VERSION '1.0';

-- *** TABLES ***
CREATE TABLE form(
  id INT NOT NULL,
  /**скрипт для открывания*/
  sOpen TEXT,
  /**скрипт для сохранения*/
  sSave TEXT,
  /**скрипт для действия*/
  sAction TEXT,
  CONSTRAINT Pk_forms PRIMARY KEY (id)
);

CREATE TABLE status(
  id INT NOT NULL,
  name VARCHAR(100) NOT NULL,
  modelId INT,
  CONSTRAINT Pk_statuses PRIMARY KEY (id)
);

CREATE TABLE statusModel(
  id INT NOT NULL,
  name VARCHAR(100) NOT NULL,
  CONSTRAINT Pk_statusModel PRIMARY KEY (id)
);

CREATE TABLE statusTransition(
  id INT NOT NULL,
  name VARCHAR(100) NOT NULL,
  statusFrom INT NOT NULL,
  statusTo INT NOT NULL,
  CONSTRAINT Pk_statusTransition PRIMARY KEY (id)
);

-- *** FOREIGN KEYS ***
ALTER TABLE status ADD CONSTRAINT Fk_status FOREIGN KEY (modelId) REFERENCES workflow.statusModel(id);
ALTER TABLE statusTransition ADD CONSTRAINT Fk_statusTransition FOREIGN KEY (statusFrom) REFERENCES workflow.status(id);
ALTER TABLE statusTransition ADD CONSTRAINT Fk_statusTransition_0 FOREIGN KEY (statusTo) REFERENCES workflow.status(id);
-- *** INDICES ***
CREATE INDEX idx_status ON status(modelId);
CREATE INDEX idx_statusTransition ON statusTransition(statusFrom);
CREATE INDEX idx_statusTransition_0 ON statusTransition(statusTo);
-- *** VIEWS ***
