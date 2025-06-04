#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Header, Path, Depends
from backend.plugin.option.service.config_service import config_service
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.response.response_code import CustomResponse
from backend.plugin.option.schema.schema_config import (
    ConfigRequest,
    ConfigDataResponse,
    SysConfigInfo,
    UpdateConfigRequest
)


from backend.common.security.jwt import DependsJwtAuth

router = APIRouter()


@router.post('/save-config', summary='保存配置并生成API Key', response_model=ResponseModel)
async def save_config(
    config_request: ConfigRequest
) -> ResponseModel:
    """
    保存配置数据并生成API Key

    :param config_request: 配置请求数据，包含名称和配置数据
    :return: 返回模型，包含状态码、消息和API Key
    """
    api_key, _ = await config_service.save_config(
        name=config_request.name,
        config_data=config_request.config_data
    )
    return response_base.success(res=CustomResponse(code=200, msg='创建成功'), data=api_key)



@router.get('/get-config', summary='获取配置', response_model=ConfigDataResponse, name='option_get_config')
async def get_config(
    api_key: str = Header(..., description='API Key')
) -> ConfigDataResponse:
    """
    获取配置数据

    :param api_key: API Key
    :return: 配置数据
    """
    config_data = await config_service.get_config(api_key=api_key)
    return ConfigDataResponse(config_data=config_data)


@router.put('/update-config', summary='更新配置', response_model=ResponseModel, name='option_update_config')
async def update_config(
    update_request: UpdateConfigRequest,
    api_key: str = Header(..., description='API Key')
) -> ResponseModel:
    """
    根据API Key更新配置数据

    :param update_request: 更新配置请求
    :param api_key: API Key
    :return: 标准响应格式，包含状态码、消息和数据
    """
    updated_config = await config_service.update_config(
        api_key=api_key,
        config_data=update_request.config_data
    )
    return response_base.success(res=CustomResponse(code=200, msg='更新成功'), data=updated_config)


@router.delete('/delete-key-by-id/{api_key_id}', summary='通过Key ID删除配置和API Key', response_model=ResponseModel, dependencies=[DependsJwtAuth])
async def delete_config_by_api_key_id(
    api_key_id: str = Path(..., description='API Key ID')
) -> ResponseModel:
    """
    通过API Key ID删除配置和API Key 是数字 不是wilmar 开头的key

    :param api_key_id: API Key ID
    :return: 删除结果
    """
    await config_service.delete_by_id(id_value=api_key_id, id_type='api_key')
    return ResponseModel(msg='删除成功')


@router.get('/get-sys-config-info', summary='获取用户历史配置和API Key信息', response_model=ResponseSchemaModel[SysConfigInfo], dependencies=[DependsJwtAuth])
async def get_sys_config_info() -> ResponseSchemaModel[SysConfigInfo]:
    """
    获取系统配置和API Key信息，API Key会被部分加密显示

    :return: 包含系统配置和API Key信息的响应
    """
    result = await config_service.get_sys_config_info()
    return response_base.success(data=SysConfigInfo(**result))


@router.get('/get-api-key/{api_key_id}', summary='获取完整的API Key', response_model=ResponseModel, dependencies=[DependsJwtAuth])
async def get_api_key(api_key_id: int = Path(..., description='API Key ID')
) -> ResponseModel:
    """
    通过API Key ID获取完整的未掩码的API Key

    :param api_key_id: API Key ID
    :return: 完整的API Key
    """
    api_key = await config_service.get_api_key_by_id(api_key_id=api_key_id)
    return response_base.success(res=CustomResponse(code=200, msg='获取成功'), data=api_key)


