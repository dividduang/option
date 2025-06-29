create table sys_api_key
(
    id             int auto_increment comment '主键 ID'
        primary key,
    uuid           varchar(50) not null comment 'UUID',
    `key`          varchar(100) not null comment 'API Key',
    name           varchar(50) not null comment 'Key名称',
    status         tinyint(1)  not null comment '状态(0停用 1正常)',
    created_time   datetime    not null comment '创建时间',
    last_used_time datetime    null comment '最后使用时间',
    constraint uuid
        unique (uuid),
    constraint api_key_unique
        unique (`key`)
)
    comment 'API Key表';

create index ix_sys_api_key_id
    on sys_api_key (id);

create table sys_api_config
(
    id           int auto_increment comment '主键 ID'
        primary key,
    uuid         varchar(50) not null comment 'UUID',
    api_key_id   int         not null comment '关联的API Key ID',
    config_data  json        not null comment '配置数据',
    created_time datetime    not null comment '创建时间',
    updated_time datetime    null comment '更新时间',
    constraint uuid
        unique (uuid),
    constraint sys_api_config_ibfk_1
        foreign key (api_key_id) references sys_api_key (id)
            on delete cascade
)
    comment 'API Key配置表';

INSERT INTO fba.sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
VALUES ('配置下发', 'Option', 'option', 7, 'eos-icons:admin', 0, '/plugins/option/views/index', null, 1, 1, 1, '', null, null, now(), null);
