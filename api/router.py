#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from backend.core.conf import settings
from backend.plugin.option.api.v1.option_api import router as option_router

v1 = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/option')

v1.include_router(option_router, tags=['option配置下发'])

