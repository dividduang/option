#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List

from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.plugin.option.model import APIKey
from backend.utils.timezone import timezone


class CRUDAPIKey(CRUDPlus[APIKey]):
    async def get_by_key(self, db: AsyncSession, key: str) -> APIKey | None:
        """
        通过 key 获取 API Key

        :param db:
        :param key:
        :return:
        """
        return await self.select_model_by_column(db, key=key)

    async def get_by_name(self, db: AsyncSession, name: str) -> APIKey | None:
        """
        通过名称获取 API Key

        :param db:
        :param name:
        :return:
        """
        return await self.select_model_by_column(db, name=name)

    async def create(self, db: AsyncSession, *, key: str, name: str) -> APIKey:
        """
        创建 API Key

        :param db:
        :param key:
        :param name:
        :return:
        """
        api_key = APIKey(key=key, name=name)
        db.add(api_key)
        await db.commit()
        await db.refresh(api_key)
        return api_key

    async def update_last_used_time(self, db: AsyncSession, key: str) -> int:
        """
        更新最后使用时间

        :param db:
        :param key:
        :return:
        """
        result = await db.execute(
            update(self.model)
            .where(self.model.key == key)
            .values(last_used_time=timezone.now())
        )
        await db.commit()
        return result.rowcount

    async def delete(self, db: AsyncSession, api_key_id: int) -> bool:
        """
        删除 API Key

        :param db:
        :param api_key_id:
        :return: 是否删除成功
        """
        api_key = await self.select_model_by_column(db, id=api_key_id)
        if api_key:
            await db.delete(api_key)
            await db.commit()
            return True
        return False

    async def get_all(self, db: AsyncSession) -> List[APIKey]:
        """
        获取所有API Key记录

        :param db:
        :return: API Key列表
        """
        result = await db.execute(select(self.model))
        return result.scalars().all()


api_key_dao: CRUDAPIKey = CRUDAPIKey(APIKey) 