#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import uuid

from pydantic import ConfigDict

from backend.common.schema import SchemaBase


class NameRequest(SchemaBase):
    name: str


class APIKeyResponse(SchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: uuid.UUID
    key: str
    name: str
    status: int
    created_time: datetime.datetime
    last_used_time: datetime.datetime | None = None 