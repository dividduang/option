#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus
from typing import List

from backend.plugin.option.model.model_config import Config


class CRUDConfig(CRUDPlus[Config]):
    async def get_by_api_key_id(self, db: AsyncSession, api_key_id: int) -> Config | None:
        """
        通过API Key ID获取配置

        :param db:
        :param api_key_id:
        :return:
        """
        return await self.select_model_by_column(db, api_key_id=api_key_id)

    async def create_or_update(self, db: AsyncSession, api_key_id: int, config_data: dict) -> Config:
        """
        创建或更新配置

        :param db:
        :param api_key_id:
        :param config_data:
        :return:
        """
        # 检查是否已存在配置
        existing_config = await self.get_by_api_key_id(db, api_key_id)
        
        if existing_config:
            # 更新现有配置
            existing_config.config_data = config_data
            await db.commit()
            await db.refresh(existing_config)
            return existing_config
        else:
            # 创建新配置
            new_config = Config(api_key_id=api_key_id, config_data=config_data)
            db.add(new_config)
            await db.commit()
            await db.refresh(new_config)
            return new_config


    async def delete_by_id(self, db: AsyncSession, config_id: int) -> bool:
        """
        通过ID删除配置

        :param db:
        :param config_id:
        :return: 是否删除成功
        """
        config = await self.select_model_by_column(db, id=config_id)
        if config:
            await db.delete(config)
            await db.commit()
            return True
        return False


config_dao: CRUDConfig = CRUDConfig(Config) 