CREATE GRAIN fileRepository VERSION '0.1';

-- *** TABLES ***
CREATE TABLE file(
  /**уникальный идентификатор, берущийся из numberSeries filesNS*/
  id VARCHAR(16) NOT NULL,
  /**имя файла под которым он был загружен*/
  name VARCHAR(512) NOT NULL,
  /**логическое значение, где True обозначает то, что предыдущие версии этого файла продолжают хранится после загрузки новой версии*/
  uploadVersioning BIT DEFAULT 'FALSE',
  CONSTRAINT pk_file_id PRIMARY KEY (id)
);

CREATE TABLE fileCounter(
  /**уникальный идентификатор, указываемый в grainsSettings, при создании настройки кластера*/
  clasterId INT NOT NULL,
  /**числовое имя последнего файла, загруженного в данный кластер*/
  latestFileName INT,
  CONSTRAINT pk_fileCounter_id PRIMARY KEY (clasterId)
);

CREATE TABLE fileVersion(
  /**уникальный идентификатор, берущийся из numberSeries fileVerNS*/
  id VARCHAR(16) NOT NULL,
  /**id файла, версия которого была добавлена/изменена*/
  fileId VARCHAR(16) NOT NULL,
  /**id кластера, все данные о котором лежат в grainssettings*/
  clasterId INT,
  /**имя файла внутри системы в числовом виде*/
  fileName VARCHAR(256) NOT NULL,
  versionMajor INT,
  versionMinor INT,
  /**если True, то файл существует и может быть скачен*/
  exist BIT,
  /**время создания лога*/
  timestamp DATETIME NOT NULL,
  CONSTRAINT pk_fileVersion_id PRIMARY KEY (id)
);

-- *** FOREIGN KEYS ***
ALTER TABLE fileVersion ADD CONSTRAINT fk_fileVersion_clasterId FOREIGN KEY (clasterId) REFERENCES fileRepository.fileCounter(clasterId);
ALTER TABLE fileVersion ADD CONSTRAINT fk_fileVersion_fileId FOREIGN KEY (fileId) REFERENCES fileRepository.file(id);
-- *** INDICES ***
-- *** VIEWS ***
