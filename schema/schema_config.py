#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ConfigRequest(BaseModel):
    """配置请求模型"""
    name: str  # API Key的名称
    config_data: Any  # 配置数据，允许任意类型


class APIKeyOnlyResponse(BaseModel):
    """只返回API Key的响应模型"""
    api_key: str  # API Key


class ConfigDataResponse(BaseModel):
    """只返回配置数据的响应模型"""
    config_data: Any  # 配置数据，允许任意类型


class UpdateConfigRequest(BaseModel):
    """更新配置请求模型"""
    config_data: Any  # 配置数据，允许任意类型


# 保留完整响应模型供将来使用
class ConfigResponse(BaseModel):
    """完整配置响应模型，包含API Key和配置数据"""
    api_key: str  # API Key
    config_data: Any  # 配置数据，允许任意类型


class APIKeyInfo(BaseModel):
    key: str
    name: str
    created_time: datetime
    last_used_time: Optional[datetime] = None


class ConfigInfo(BaseModel):
    api_key_id: int
    api_key: APIKeyInfo


class SysConfigInfo(BaseModel):
    configs: List[ConfigInfo]
    model_config = ConfigDict(from_attributes=True)
