#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Dict, List, Tuple, Any, Callable, TypeVar
from functools import wraps

from backend.common.exception import errors
from backend.plugin.option.crud.crud_config import config_dao
from backend.plugin.option.crud.crud_api_key import api_key_dao
from backend.plugin.option.service.api_key_service import APIKeyService
from backend.database.db import async_db_session

# 定义类型变量用于装饰器
T = TypeVar('T')


def db_transaction(func: Callable[..., T]) -> Callable[..., T]:
    """
    数据库事务装饰器，简化数据库会话管理和错误处理
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        async with async_db_session() as db:
            try:
                # 将数据库会话添加到参数中
                kwargs['db'] = db
                result = await func(*args, **kwargs)
                return result
            except errors.NotFoundError:
                await db.rollback()
                raise
            except Exception as e:
                await db.rollback()
                # 如果是自定义错误，直接抛出
                if isinstance(e, errors.CustomError):
                    raise
                # 否则包装为 ForbiddenError
                raise errors.ForbiddenError(msg=f'操作失败: {str(e)}')
    return wrapper


class ConfigService:
    @staticmethod
    @db_transaction
    async def save_config(*, db: Any, name: str, config_data: Any) -> Tuple[str, Any]:
        """
        保存配置并生成API Key

        :param db: 数据库会话
        :param name: API Key名称
        :param config_data: 配置数据
        :return: (API Key, 配置数据)
        """
        # 生成新的API Key
        api_key = APIKeyService.generate_api_key()

        # 创建API Key记录
        api_key_record = await api_key_dao.create(db, key=api_key, name=name)
        if not api_key_record:
            raise errors.ForbiddenError(msg='API Key创建失败')

        # 保存配置
        config = await config_dao.create_or_update(db, api_key_record.id, config_data)
        if not config:
            raise errors.ForbiddenError(msg='配置保存失败')

        return api_key, config.config_data

    @staticmethod
    @db_transaction
    async def get_config(*, db: Any, api_key: str) -> Any:
        """
        获取配置

        :param db: 数据库会话
        :param api_key: API Key
        :return: 配置数据
        """
        # 验证API Key
        key_record = await APIKeyService.get_api_key_record(db, api_key)
        if not key_record:
            raise errors.ForbiddenError(msg='无效的API Key')
        if not key_record.status:
            raise errors.ForbiddenError(msg='API Key已被禁用')

        # 获取配置
        config = await config_dao.get_by_api_key_id(db, key_record.id)
        if not config:
            raise errors.NotFoundError(msg='未找到配置数据')

        # 更新最后使用时间
        await api_key_dao.update_last_used_time(db, api_key)
        return config.config_data

    @staticmethod
    @db_transaction
    async def update_config(*, db: Any, api_key: str, config_data: Any) -> Any:
        """
        根据API Key更新配置数据

        :param db: 数据库会话
        :param api_key: API Key
        :param config_data: 新的配置数据
        :return: 更新后的配置数据
        """
        # 验证API Key
        key_record = await APIKeyService.get_api_key_record(db, api_key)
        if not key_record:
            raise errors.ForbiddenError(msg='无效的API Key')
        if not key_record.status:
            raise errors.ForbiddenError(msg='API Key已被禁用')

        # 获取配置
        config = await config_dao.get_by_api_key_id(db, key_record.id)
        if not config:
            raise errors.NotFoundError(msg='未找到配置数据')

        # 更新配置
        config.config_data = config_data
        await db.commit()
        await db.refresh(config)

        # 更新最后使用时间
        await api_key_dao.update_last_used_time(db, api_key)

        return config.config_data

    @staticmethod
    async def _delete_config_and_api_key(db: Any, config=None, api_key=None) -> None:
        """
        内部方法：删除配置和API Key

        :param db: 数据库会话
        :param config: 配置对象
        :param api_key: API Key对象
        """
        # 先删除配置
        if config:
            await db.delete(config)
            await db.commit()

        # 再删除API Key
        if api_key:
            await db.delete(api_key)
            await db.commit()

    @staticmethod
    @db_transaction
    async def delete_config(*, db: Any, api_key: str) -> bool:
        """
        删除配置和API Key

        :param db: 数据库会话
        :param api_key: API Key
        :return: 是否删除成功
        """
        # 验证API Key
        key_record = await APIKeyService.get_api_key_record(db, api_key)
        if not key_record:
            raise errors.ForbiddenError(msg='无效的API Key')

        # 获取配置
        config = await config_dao.get_by_api_key_id(db, key_record.id)

        # 删除配置和API Key
        await ConfigService._delete_config_and_api_key(db, config, key_record)
        return True

    @staticmethod
    @db_transaction
    async def delete_by_id(*, db: Any, id_value: int, id_type: str = 'config') -> bool:
        """
        通过ID删除配置和API Key

        :param db: 数据库会话
        :param id_value: ID值
        :param id_type: ID类型，'config' 或 'api_key'
        :return: 是否删除成功
        """
        config = None
        api_key = None

        if id_type == 'config':
            # 获取配置
            config = await config_dao.select_model_by_column(db, id=id_value)
            if not config:
                raise errors.NotFoundError(msg=f'未找到ID为 {id_value} 的配置数据')

            # 获取API Key
            api_key = await api_key_dao.select_model_by_column(db, id=config.api_key_id)
            if not api_key:
                raise errors.NotFoundError(msg=f'未找到ID为 {config.api_key_id} 的API Key')
        else:  # id_type == 'api_key'
            # 获取API Key
            api_key = await api_key_dao.select_model_by_column(db, id=id_value)
            if not api_key:
                raise errors.NotFoundError(msg=f'未找到ID为 {id_value} 的API Key')

            # 获取配置
            config = await config_dao.get_by_api_key_id(db, id_value)

        # 删除配置和API Key
        await ConfigService._delete_config_and_api_key(db, config, api_key)
        return True

    # 兼容旧的方法名
    @staticmethod
    async def delete_config_by_id(*, config_id: int) -> bool:
        """兼容旧的方法名"""
        return await ConfigService.delete_by_id(id_value=config_id, id_type='config')

    # 兼容旧的方法名
    @staticmethod
    async def delete_config_by_api_key_id(*, api_key_id: int) -> bool:
        """兼容旧的方法名"""
        return await ConfigService.delete_by_id(id_value=api_key_id, id_type='api_key')

    @staticmethod
    def _mask_api_key(api_key: str) -> str:
        """
        内部方法：对API Key进行掉码处理

        :param api_key: 原始API Key
        :return: 掉码后的API Key
        """
        prefix = api_key[:11]  # 'wilmar-'
        suffix = api_key[39:]  # 最后8位
        return prefix + '*' * 28 + suffix

    @staticmethod
    def _build_config_info(api_key_record: Any, config_obj: Any = None) -> dict:
        """
        内部方法：构建配置信息字典

        :param api_key_record: API Key记录
        :param config_obj: 配置对象
        :return: 配置信息字典
        """
        # 处理API Key的显示
        masked_key = ConfigService._mask_api_key(api_key_record.key)

        return {
            'api_key_id': api_key_record.id,
            'api_key': {
                'key': masked_key,
                'name': api_key_record.name,
                'created_time': api_key_record.created_time,
                'last_used_time': api_key_record.last_used_time
            }
        }

    @staticmethod
    @db_transaction
    async def update_config(*, db: Any, api_key: str, config_data: Any) -> Any:
        """
        根据API Key更新配置数据

        :param db: 数据库会话
        :param api_key: API Key
        :param config_data: 新的配置数据
        :return: 更新后的配置数据
        """
        # 验证API Key
        key_record = await APIKeyService.get_api_key_record(db, api_key)
        if not key_record:
            raise errors.ForbiddenError(msg='无效的API Key')
        if not key_record.status:
            raise errors.ForbiddenError(msg='API Key已被禁用')

        # 获取配置
        config = await config_dao.get_by_api_key_id(db, key_record.id)
        if not config:
            raise errors.NotFoundError(msg='未找到配置数据')

        # 更新配置
        config.config_data = config_data
        await db.commit()
        await db.refresh(config)

        # 更新最后使用时间
        await api_key_dao.update_last_used_time(db, api_key)

        return config.config_data



    @staticmethod
    @db_transaction
    async def get_sys_config_info(*, db: Any) -> dict:
        """
        获取系统配置和API Key信息，API Key会被部分加密显示

        :param db: 数据库会话
        :return: 包含系统配置和API Key信息的字典
        """
        # 获取所有API Key记录
        api_key_records = await api_key_dao.get_all(db)
        if not api_key_records:
            return {
                'configs': []
            }

        configs_list = []
        for api_key_record in api_key_records:
            # 获取配置
            config_obj = await config_dao.get_by_api_key_id(db, api_key_record.id)

            # 构建配置信息
            config_info = ConfigService._build_config_info(api_key_record, config_obj)
            configs_list.append(config_info)

        return {
            'configs': configs_list
        }


config_service: ConfigService = ConfigService()