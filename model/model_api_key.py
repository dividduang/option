#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.common.model import DataClassBase, id_key
from backend.database.db import uuid4_str
from backend.utils.timezone import timezone


class APIKey(DataClassBase):
    """API Key表"""

    __tablename__ = 'sys_api_key'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True, comment='API Key')
    name: Mapped[str] = mapped_column(String(50), comment='Key名称')
    status: Mapped[int] = mapped_column(default=1, comment='状态(0停用 1正常)')
    created_time: Mapped[datetime] = mapped_column(init=False, default_factory=timezone.now, comment='创建时间')
    last_used_time: Mapped[datetime | None] = mapped_column(init=False, onupdate=timezone.now, comment='最后使用时间')

    # 关联关系
    configs = relationship("backend.plugin.option.model.model_config.Config", back_populates="api_key")