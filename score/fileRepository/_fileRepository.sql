CREATE GRAIN fileRepository VERSION '0.1';

-- *** TABLES ***
CREATE TABLE file(
  id VARCHAR(16) NOT NULL,
  name VARCHAR(512) NOT NULL,
  uploadVersioning BIT DEFAULT 'FALSE',
  CONSTRAINT pk_file_id PRIMARY KEY (id)
);

CREATE TABLE fileVersion(
  id VARCHAR(16) NOT NULL,
  fileId VARCHAR(16) NOT NULL,
  clasterId INT,
  fileName VARCHAR(256) NOT NULL,
  versionMajor INT,
  versionMinor INT,
  exist BIT,
  timestamp DATETIME NOT NULL,
  CONSTRAINT pk_fileVersion_id PRIMARY KEY (id)
);

CREATE TABLE fileCounter(
  clasterId INT NOT NULL,
  latestFileName INT,
  CONSTRAINT pk_fileCounter_id PRIMARY KEY (clasterId)
);

-- *** FOREIGN KEYS ***
ALTER TABLE fileVersion ADD CONSTRAINT fk_fileVersion_clasterId FOREIGN KEY (clasterId) REFERENCES fileRepository.fileCounter(clasterId);
ALTER TABLE fileVersion ADD CONSTRAINT fk_fileVersion_fileId FOREIGN KEY (fileId) REFERENCES fileRepository.file(id);
-- *** INDICES ***
-- *** VIEWS ***
