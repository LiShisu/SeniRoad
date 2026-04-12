from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.models import User, Location
from sqlalchemy.orm import Session
import pytest
from datetime import datetime

client = TestClient(app)

@pytest.fixture
def db_session():
    """创建数据库会话"""
    from app.database import Base, engine
    Base.metadata.create_all(bind=engine)
    db = Session(bind=engine)
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_token(db_session):
    """获取认证令牌"""
    # 注册用户
    client.post("/api/v1/auth/register", json={
        "phone": "13800138000",
        "password": "123456",
        "nickname": "测试用户",
        "role": "elderly"
    })
    
    # 登录获取令牌
    response = client.post("/api/v1/auth/login", data={
        "username": "13800138000",
        "password": "123456"
    })
    return response.json()["access_token"]

def test_update_location(auth_token):
    """测试更新实时位置"""
    response = client.post("/api/v1/locations/update", json={
        "latitude": 39.90923,
        "longitude": 116.397428,
        "address": "北京市东城区",
        "accuracy": 10.0
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 201
    assert response.json()["latitude"] == 39.90923
    assert response.json()["longitude"] == 116.397428
    assert response.json()["address"] == "北京市东城区"
    assert response.json()["accuracy"] == 10.0

def test_get_location_history(auth_token):
    """测试查询历史轨迹"""
    # 更新位置
    client.post("/api/v1/locations/update", json={
        "latitude": 39.90923,
        "longitude": 116.397428,
        "address": "北京市东城区",
        "accuracy": 10.0
    }, headers={"Authorization": f"Bearer {auth_token}"})
    
    # 获取历史轨迹
    response = client.get("/api/v1/locations/history", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["latitude"] == 39.90923
    assert response.json()[0]["longitude"] == 116.397428

def test_get_latest_location(auth_token):
    """测试获取最新位置"""
    # 更新位置
    client.post("/api/v1/locations/update", json={
        "latitude": 39.90923,
        "longitude": 116.397428,
        "address": "北京市东城区",
        "accuracy": 10.0
    }, headers={"Authorization": f"Bearer {auth_token}"})
    
    # 获取最新位置
    response = client.get("/api/v1/locations/latest", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    assert response.json()["latitude"] == 39.90923
    assert response.json()["longitude"] == 116.397428
