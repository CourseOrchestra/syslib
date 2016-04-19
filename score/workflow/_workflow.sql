CREATE GRAIN workflow VERSION '1.0';

-- *** TABLES ***

CREATE TABLe processes(
	processKey varchar(30) NOT NULL,
	processName varchar(100) NOT NULL,
	CONSTRAINT pk_processes PRIMARY KEY (processKey)
);

CREATE TABLE form(
  processKey varchar(30) NOT NULL,
  id varchar(30) NOT NULL,
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

CREATE TABLE processStatusModel(
	processKey varchar(30) NOT NULL,
	modelId varchar(50) NOT NULL,
	CONSTRAINT pk_processStatusModel PRIMARY KEY (processKey)
);


CREATE TABLE matchingCircuit(
	processKey varchar(30) NOT NULL,
	taskKey varchar(30) NULL,
	id int NOT NULL,
	name varchar(50) NOT NULL,
	type varchar(50) NOT NULL,
	assJSON TEXT,
	number varchar(30) NOT NULL,
	sort varchar(100) NOT NULL,
	CONSTRAINT pk_matchingCircuit PRIMARY KEY(processKey,id)
);

CREATE TABLE status(
  id VARCHAR(50) NOT NULL,
  name VARCHAR(100) NOT NULL,
  modelId VARCHAR(50) NOT NULL,
  varName varchar(50),
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

CREATE TABLE userGroup(
	userId VARCHAR(36) NOT NULL,
	groupId VARCHAR(36) NOT NULL,
	CONSTRAINT PK_userGroup PRIMARY KEY (userId, groupId)
);

CREATE TABLE groups(
	groupId VARCHAR(36) NOT NULL,
	groupName VARCHAR(100) NOT NULL,
	number VARCHAR(30) NOT NULL,
	sort VARCHAR(100) NOT NULL,
	CONSTRAINT PK_group PRIMARY KEY(groupId)
);



create table act_ge_property (
    name_ varchar(64) not null,
    value_ varchar(300),
    rev_ int,
    constraint pk_act_ge_property primary key (name_)
)with no version check;

create table act_ge_bytearray (
    id_ varchar(64) not null,
    rev_ int,
    name_ varchar(255),
    deployment_id_ varchar(64),
    bytes_ blob,
    generated_ bit,
    constraint pk_bytearray primary key (id_)
)with no version check;

create table act_re_deployment (
    id_ varchar(64) not null,
    name_ varchar(255),
    category_ varchar(255),
    tenant_id_ varchar(255) default '',
    deploy_time_ datetime,
    constraint pk_deployment primary key (id_)
)with no version check;

create table act_re_model (
    id_ varchar(64) not null,
    rev_ int,
    name_ varchar(255),
    key_ varchar(255),
    category_ varchar(255),
    create_time_ datetime,
    last_update_time_ datetime,
    version_ int,
    meta_info_ varchar(4000),
    deployment_id_ varchar(64),
    editor_source_value_id_ varchar(64) not null default '',
    editor_source_extra_value_id_ varchar(64) not null default '',
    tenant_id_ varchar(255) default '',
    constraint pk_model primary key (id_)
)with no version check;

create table act_ru_execution (
    id_ varchar(64) not null,
    rev_ int,
    proc_inst_id_ varchar(64) not null default '',
    business_key_ varchar(255),
    parent_id_ varchar(64),
    proc_def_id_ varchar(64) not null default '',
    super_exec_ varchar(64),
    act_id_ varchar(255),
    is_active_ bit,
    is_concurrent_ bit,
    is_scope_ bit,
    is_event_scope_ bit,
    suspension_state_ int,
    cached_ent_state_ int,
    tenant_id_ varchar(255) default '',
    name_ varchar(255),
    constraint pk_execution primary key (id_)
)with no version check;

create table act_ru_job (
    id_ varchar(64) not null,
    rev_ int,
    type_ varchar(255) not null,
    lock_exp_time_ datetime,
    lock_owner_ varchar(255),
    exclusive_ bit,
    execution_id_ varchar(64),
    process_instance_id_ varchar(64),
    proc_def_id_ varchar(64),
    retries_ int,
    exception_stack_id_ varchar(64) not null default '',
    exception_msg_ varchar(4000),
    duedate_ datetime,
    repeat_ varchar(255),
    handler_type_ varchar(255),
    handler_cfg_ varchar(4000),
    tenant_id_ varchar(255) default '',
    constraint pk_job primary key (id_)
)with no version check;

create table act_re_procdef (
    id_ varchar(64) not null,
    rev_ int,
    category_ varchar(255),
    name_ varchar(255),
    key_ varchar(255) not null,
    version_ int not null,
    deployment_id_ varchar(64),
    resource_name_ varchar(4000),
    dgrm_resource_name_ varchar(4000),
    description_ varchar(4000),
    has_start_form_key_ bit,
    suspension_state_ int,
    tenant_id_ varchar(255) default '',
    constraint pk_procdef primary key (id_)
)with no version check;

create table act_ru_task(
	id_ varchar(64) not null,
	rev_ int,
	execution_id_ varchar(64) not null default '',
	proc_inst_id_ varchar(64) not null default '',
	proc_def_id_ varchar(64) not null default '',
	name_ varchar(255),
	parent_task_id_ varchar(64),
	description_ varchar(4000),
	task_def_key_ varchar(255),
	owner_ varchar(255),
	assignee_ varchar(255),
	delegation_ varchar(64),
	priority_ int,
	create_time_ datetime not null default getdate(),
	due_date_ datetime,
	category_ varchar(255),
	suspension_state_ int,
	tenant_id_ varchar(255),
	form_key_ varchar(255),
	constraint pk_act_ru_task primary key (id_)
) with no version check;

create table act_ru_identitylink (
    id_ varchar(64) not null,
    rev_ int,
    group_id_ varchar(255),
    type_ varchar(255),
    user_id_ varchar(255) not null default '',
    task_id_ varchar(64),
    proc_inst_id_ varchar(64) not null default '',
    proc_def_id_ varchar (64),
    constraint pk_identitylink primary key (id_)
)with no version check;

create table act_ru_variable (
    id_ varchar(64) not null,
    rev_ int,
    type_ varchar(255) not null,
    name_ varchar(255) not null,
    execution_id_ varchar(64) not null default '',
    proc_inst_id_ varchar(64) not null default '',
    task_id_ varchar(64),
    bytearray_id_ varchar(64),
    double_ real,
    long_ int,
    text_ varchar(4000),
    text2_ varchar(4000),
    constraint pk_variable primary key (id_)
)with no version check;

create table act_ru_event_subscr (
    id_ varchar(64) not null,
    rev_ int,
    event_type_ varchar(255) not null,
    event_name_ varchar(255),
    execution_id_ varchar(64) not null default '',
    proc_inst_id_ varchar(64),
    activity_id_ varchar(64),
    configuration_ varchar(255) not null default '',
    created_ datetime not null,
    proc_def_id_ varchar(64),
    tenant_id_ varchar(255) default '',
    constraint pk_event_subsc primary key (id_)
)with no version check;

create table act_evt_log (
    log_nr_ int not null identity,
    type_ varchar(64),
    proc_def_id_ varchar(64),
    proc_inst_id_ varchar(64),
    execution_id_ varchar(64),
    task_id_ varchar(64),
    time_stamp_ datetime not null,
    user_id_ varchar(255),
    data_ blob,
    lock_owner_ varchar(255),
    lock_time_ datetime null,
    is_processed_ int default 0,
	constraint pk_event_log primary key(log_nr_)
)with no version check;


create table act_hi_procinst (
    id_ varchar(64) not null,
    proc_inst_id_ varchar(64) not null,
    business_key_ varchar(255),
    proc_def_id_ varchar(64) not null,
    start_time_ datetime not null,
    end_time_ datetime,
    duration_ real,
    start_user_id_ varchar(255),
    start_act_id_ varchar(255),
    end_act_id_ varchar(255),
    super_process_instance_id_ varchar(64),
    delete_reason_ varchar(4000),
    tenant_id_ varchar(255) default '',
    name_ varchar(255),
    constraint pk_hi_procinst primary key (id_)
)with no version check;

create table act_hi_actinst (
    id_ varchar(64) not null,
    proc_def_id_ varchar(64) not null,
    proc_inst_id_ varchar(64) not null,
    execution_id_ varchar(64) not null,
    act_id_ varchar(255) not null,
    task_id_ varchar(64),
    call_proc_inst_id_ varchar(64),
    act_name_ varchar(255),
    act_type_ varchar(255) not null,
    assignee_ varchar(255),
    start_time_ datetime not null,
    end_time_ datetime,
    duration_ real,
    tenant_id_ varchar(255) default '',
    constraint pk_hi_actinst primary key (id_)
)with no version check;

create table act_hi_taskinst (
    id_ varchar(64) not null,
    proc_def_id_ varchar(64),
    task_def_key_ varchar(255),
    proc_inst_id_ varchar(64),
    execution_id_ varchar(64),
    name_ varchar(255),
    parent_task_id_ varchar(64),
    description_ varchar(4000),
    owner_ varchar(255),
    assignee_ varchar(255),
    start_time_ datetime not null,
    claim_time_ datetime,
    end_time_ datetime,
    duration_ real,
    delete_reason_ varchar(4000),
    priority_ int,
    due_date_ datetime,
    form_key_ varchar(255),
    category_ varchar(255),
    tenant_id_ varchar(255) default '',
    constraint pk_hi_taskinst primary key (id_)
)with no version check;

create table act_hi_varinst (
    id_ varchar(64) not null,
    proc_inst_id_ varchar(64) not null default '',
    execution_id_ varchar(64),
    task_id_ varchar(64),
    name_ varchar(255) not null,
    var_type_ varchar(100) not null default '',
    rev_ int,
    bytearray_id_ varchar(64),
    double_ real,
    long_ int,
    text_ varchar(4000),
    text2_ varchar(4000),
    create_time_ datetime,
    last_updated_time_ datetime,
    constraint pk_hi_varinst primary key (id_)
)with no version check;

create table act_hi_detail (
    id_ varchar(64) not null,
    type_ varchar(255) not null,
    proc_inst_id_ varchar(64) not null default '',
    execution_id_ varchar(64),
    task_id_ varchar(64),
    act_inst_id_ varchar(64),
    name_ varchar(255) not null,
    var_type_ varchar(64),
    rev_ int,
    time_ datetime not null,
    bytearray_id_ varchar(64),
    double_ real,
    long_ int,
    text_ varchar(4000),
    text2_ varchar(4000),
    constraint pk_hi_detail primary key (id_)
)with no version check;

create table act_hi_comment (
    id_ varchar(64) not null,
    type_ varchar(255),
    time_ datetime not null,
    user_id_ varchar(255),
    task_id_ varchar(64),
    proc_inst_id_ varchar(64),
    action_ varchar(255),
    message_ varchar(4000),
    full_msg_ blob,
    constraint pk_hi_comment primary key (id_)
)with no version check;

create table act_hi_attachment (
    id_ varchar(64) not null,
    rev_ int,
    user_id_ varchar(255),
    name_ varchar(255),
    description_ varchar(4000),
    type_ varchar(255),
    task_id_ varchar(64),
    proc_inst_id_ varchar(64),
    url_ varchar(4000),
    content_id_ varchar(64),
    constraint pk_hi_attach primary key (id_)
)with no version check;

create table act_hi_identitylink (
    id_ varchar(64) not null,
    group_id_ varchar(255),
    type_ varchar(255),
    user_id_ varchar(255) not null default '',
    task_id_ varchar(64),
    proc_inst_id_ varchar(64) not null default '',
    constraint pk_hi_ident primary key (id_)
)with no version check;



create table act_id_group (
    id_ varchar(64) not null,
    rev_ int,
    name_ varchar(255),
    type_ varchar(255),
    constraint pk_id_group primary key (id_)
)with no version check;

create table act_id_membership (
    user_id_ varchar(64) not null,
    group_id_ varchar(64) not null,
    constraint pk_id_member primary key (user_id_, group_id_)
)with no version check;

create table act_id_user (
    id_ varchar(64) not null,
    rev_ int,
    first_ varchar(255),
    last_ varchar(255),
    email_ varchar(255),
    pwd_ varchar(255),
    picture_id_ varchar(64),
    constraint pk_id_user primary key (id_)
)with no version check;

create table act_id_info (
    id_ varchar(64) not null,
    rev_ int,
    user_id_ varchar(64),
    type_ varchar(64),
    key_ varchar(255),
    value_ varchar(255),
    password_ blob,
    parent_id_ varchar(255),
    constraint pk_id_info primary key (id_)
)with no version check;

create table act_task_links(
	task_id_ varchar(64) not null,
	users TEXT,
	groups TEXT,
	constraint pk_task_links primary key (task_id_)
) with no version check;

create table act_proc_version(
	processKey varchar(255) not null,
	process_id varchar(64) not null,
	constraint pk_proc_version primary key(processKey)
) with no version check;

create view view_launched_process as
select execs.id_ as id_, execs.proc_inst_id_ as proc_inst_id_, procdef.name_ as processName, vars.text_ as processDescription
from workflow.act_ru_execution as execs
inner join workflow.act_re_procdef as procdef
on execs.proc_def_id_ = procdef.id_
inner join workflow.act_ru_variable as vars
on execs.proc_inst_id_ = vars.proc_inst_id_ and vars.name_ = 'processDescription'
where execs.id_ = execs.proc_inst_id_;

create view view_finished_process as
select procs.id_ as id_, procs.proc_inst_id_ as proc_inst_id_, procdef.name_ as processName, vars.text_ as processDescription,
	   procs.delete_reason_ as delete_reason, procs.end_time_ as end_time
from workflow.act_hi_procinst as procs
inner join workflow.act_re_procdef as procdef
on procs.proc_def_id_ = procdef.id_
inner join workflow.act_hi_varinst as vars
on procs.proc_inst_id_ = vars.proc_inst_id_ and vars.name_ = 'processDescription'
;

create view view_finished_tasks as
select tasks.id_ as id_, tasks.name_ as name_ , tasks.assignee_ as assignee_, tasks.end_time_ as end_time_, procdef.name_ as processName, vars.text_ as processDescription
from workflow.act_hi_taskinst as tasks
inner join workflow.act_re_procdef as procdef
on tasks.proc_def_id_ = procdef.id_
inner join workflow.act_hi_varinst as vars
on tasks.proc_inst_id_ = vars.proc_inst_id_ and vars.name_ = 'processDescription'
;

create view view_task_links as
select tasks.id_ as id_, tasks.execution_id_ as execution_id_, tasks.proc_inst_id_ as proc_inst_id_,
	   tasks.proc_def_id_ as proc_def_id_, tasks.name_ as name_, tasks.parent_task_id_ as parent_task_id_,
	   tasks.description_ as description_, tasks.task_def_key_ as task_def_key_, tasks.owner_ as owner_,
	   tasks.assignee_ as assignee_, tasks.delegation_ as delegation_, tasks.priority_ as  priority_,
	   tasks.create_time_ as create_time_, tasks.due_date_ as due_date_, tasks.category_ as category_,
	   tasks.suspension_state_ as suspension_state_, tasks.tenant_id_ as tenant_id_, tasks.form_key_ as form_key_,
	   links.users as users, links.groups as groups, procdef.name_ as processName, procdef.key_ as processKey,
	   vars.text_ as processDescription
from workflow.act_ru_task as tasks
left join workflow.act_task_links as links
on tasks.id_ = links.task_id_
inner join workflow.act_re_procdef as procdef
on tasks.proc_def_id_ = procdef.id_
inner join workflow.act_ru_variable as vars
on tasks.proc_inst_id_ = vars.proc_inst_id_ and vars.name_ = 'processDescription';


create view view_subjects as
select distinct subjects.sid as sid, subjects.name as name
from security.subjects as subjects
inner join celesta.userroles as userroles
on subjects.sid = userroles.userid
where roleid = 'workflowDev' or roleid = 'workflowUser';

create index act_idx_task_create on act_ru_task(create_time_);
create index act_idx_ident_lnk_user on act_ru_identitylink(user_id_);
create index act_idx_event_subscr_config_ on act_ru_event_subscr(configuration_);


alter table act_ge_bytearray
    add constraint act_fk_bytearr_depl
    foreign key (deployment_id_) 
    references act_re_deployment (id_);


    
create index act_idx_exe_procinst on act_ru_execution(proc_inst_id_);
alter table act_ru_execution
    add constraint act_fk_exe_procinst 
    foreign key (proc_inst_id_) 
    references act_ru_execution (id_);

alter table act_ru_execution
    add constraint act_fk_exe_parent
    foreign key (parent_id_) 
    references act_ru_execution (id_);
    
alter table act_ru_execution
    add constraint act_fk_exe_super
    foreign key (super_exec_) 
    references act_ru_execution (id_);

create index act_idx_exe_procdef on act_ru_execution(proc_def_id_); 
alter table act_ru_execution
    add constraint act_fk_exe_procdef 
    foreign key (proc_def_id_) 
    references act_re_procdef (id_);    
    

alter table act_ru_identitylink
    add constraint act_fk_tskass_task
    foreign key (task_id_) 
    references act_ru_task (id_);
    
alter table act_ru_identitylink
    add constraint act_fk_athrz_procedef
    foreign key (proc_def_id_) 
    references act_re_procdef (id_);
    
create index act_idx_idl_procinst on act_ru_identitylink(proc_inst_id_);
alter table act_ru_identitylink
    add constraint act_fk_idl_procinst
    foreign key (proc_inst_id_) 
    references act_ru_execution (id_);    
    
create index act_idx_task_exec on act_ru_task(execution_id_);
alter table act_ru_task
    add constraint act_fk_task_exe
    foreign key (execution_id_)
    references act_ru_execution (id_);
    
create index act_idx_task_procinst on act_ru_task(proc_inst_id_);
alter table act_ru_task
    add constraint act_fk_task_procinst
    foreign key (proc_inst_id_)
    references act_ru_execution (id_);
    
create index act_idx_task_procdef on act_ru_task(proc_def_id_);
alter table act_ru_task
  add constraint act_fk_task_procdef
  foreign key (proc_def_id_)
  references act_re_procdef (id_);
  
create index act_idx_var_exe on act_ru_variable(execution_id_);
alter table act_ru_variable 
    add constraint act_fk_var_exe
    foreign key (execution_id_) 
    references act_ru_execution (id_);

create index act_idx_var_procinst on act_ru_variable(proc_inst_id_);
alter table act_ru_variable
    add constraint act_fk_var_procinst
    foreign key (proc_inst_id_)
    references act_ru_execution(id_);

alter table act_ru_variable 
    add constraint act_fk_var_bytearray 
    foreign key (bytearray_id_) 
    references act_ge_bytearray (id_);

create index act_idx_job_exception on act_ru_job(exception_stack_id_);
alter table act_ru_job 
    add constraint act_fk_job_exception
    foreign key (exception_stack_id_) 
    references act_ge_bytearray (id_);

create index act_idx_event_subscr on act_ru_event_subscr(execution_id_);
alter table act_ru_event_subscr
    add constraint act_fk_event_exec
    foreign key (execution_id_)
    references act_ru_execution(id_);

create index act_idx_model_source on act_re_model(editor_source_value_id_);
alter table act_re_model 
    add constraint act_fk_model_source 
    foreign key (editor_source_value_id_) 
    references act_ge_bytearray (id_);

create index act_idx_model_source_extra on act_re_model(editor_source_extra_value_id_);
alter table act_re_model 
    add constraint act_fk_model_source_extra 
    foreign key (editor_source_extra_value_id_) 
    references act_ge_bytearray (id_);
      
alter table act_re_model 
    add constraint act_fk_model_deployment 
    foreign key (deployment_id_) 
    references act_re_deployment (id_); 

create index act_idx_hi_act_inst_start on act_hi_actinst(start_time_);
create index act_idx_hi_detail_proc_inst on act_hi_detail(proc_inst_id_);
create index act_idx_hi_detail_time on act_hi_detail(time_);
create index act_idx_hi_detail_name on act_hi_detail(name_);
create index act_idx_hi_procvar_proc_inst on act_hi_varinst(proc_inst_id_);
create index act_idx_hi_procvar_name_type on act_hi_varinst(name_, var_type_);
create index act_idx_hi_act_inst_procinst on act_hi_actinst(proc_inst_id_, act_id_);
create index act_idx_hi_act_inst_exec on act_hi_actinst(execution_id_, act_id_);
create index act_idx_hi_ident_lnk_user on act_hi_identitylink(user_id_);
create index act_idx_hi_ident_lnk_procinst on act_hi_identitylink(proc_inst_id_);


-- *** FOREIGN KEYS ***
ALTER TABLE userGroup ADD CONSTRAINT fk_users_groups FOREIGN KEY (groupId) REFERENCES workflow.groups(groupId);
ALTER TABLE status ADD CONSTRAINT fk_status FOREIGN KEY (modelId) REFERENCES workflow.statusModel(id);
ALTER TABLE matchingCircuit ADD CONSTRAINT fk_procKey FOREIGN KEY (processKey) REFERENCES workflow.processes(processKey);
ALTER TABLE statusTransition ADD CONSTRAINT fk_statustransition_status FOREIGN KEY (statusFrom, modelFrom) REFERENCES workflow.status(id, modelId);
ALTER TABLE statusTransition ADD CONSTRAINT fk_statustransition_status2 FOREIGN KEY (statusTo, modelTo) REFERENCES workflow.status(id, modelId);
ALTER TABLE processStatusModel ADD CONSTRAINT fk_procStatModel FOREIGN KEY (modelId) REFERENCES workflow.statusModel(id);
ALTER TABLE act_proc_version ADD CONSTRAINT fk_proc_version FOREIGN KEY (process_id) references workflow.act_re_procdef(id_);
-- *** INDICES ***
CREATE INDEX idx_statusTransition ON statusTransition(statusFrom, modelFrom);
CREATE INDEX idx_statusTransition_0 ON statusTransition(statusTo, modelTo);
-- *** VIEWS ***
