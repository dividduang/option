#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import String, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.common.model import DataClassBase, id_key
from backend.database.db import uuid4_str
from backend.utils.timezone import timezone


class Config(DataClassBase):
    """API Key配置表"""

    __tablename__ = 'sys_api_config'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    api_key_id: Mapped[int] = mapped_column(ForeignKey("sys_api_key.id"), comment='关联的API Key ID')
    config_data: Mapped[dict] = mapped_column(JSON, comment='配置数据')
    created_time: Mapped[datetime] = mapped_column(init=False, default_factory=timezone.now, comment='创建时间')
    updated_time: Mapped[datetime] = mapped_column(init=False, default_factory=timezone.now, onupdate=timezone.now, comment='更新时间')

    # 关联关系
    api_key = relationship("backend.plugin.option.model.model_api_key.APIKey", back_populates="configs")