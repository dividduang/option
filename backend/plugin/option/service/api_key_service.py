#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import uuid

from backend.common.exception import errors
from backend.plugin.option.crud.crud_api_key import api_key_dao
from backend.database.db import async_db_session
from backend.plugin.option.schema.schema_api_key import NameRequest


class APIKeyService:
    @staticmethod
    def generate_api_key() -> str:
        """
        生成API Key

        :return:
        """
        return 'wilmar-' + str(uuid.uuid4())

    @staticmethod
    async def create_api_key(*, obj: NameRequest) -> str:
        """
        创建API Key

        :param obj:
        :return:
        """
        async with async_db_session() as db:
            # 检查名称是否已存在
            existing_key = await api_key_dao.get_by_name(db, obj.name)
            if existing_key:
                raise errors.ForbiddenError(msg='该名称已存在')

            # 生成新的API Key
            api_key = APIKeyService.generate_api_key()

            # 创建API Key记录
            await api_key_dao.create(db, key=api_key, name=obj.name)
            return api_key

    @staticmethod
    async def get_api_key_record(db, api_key: str):
        """
        获取API Key记录

        :param db: 数据库会话
        :param api_key: API Key
        :return: API Key记录或None
        """
        key_record = await api_key_dao.get_by_key(db, api_key)
        return key_record

    @staticmethod
    async def verify_api_key(*, api_key: str) -> bool:
        """
        验证API Key

        :param api_key: API Key
        :return: 是否有效
        """
        async with async_db_session() as db:
            key_record = await APIKeyService.get_api_key_record(db, api_key)
            if not key_record or not key_record.status:
                return False

            # 更新最后使用时间
            await api_key_dao.update_last_used_time(db, api_key)
            return True


api_key_service: APIKeyService = APIKeyService()