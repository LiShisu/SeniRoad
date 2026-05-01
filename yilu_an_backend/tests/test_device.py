from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from sqlalchemy.orm import Session
import pytest

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

def test_create_device(auth_token):
    """测试创建设备"""
    response = client.post("/api/v1/devices/", json={
        "user_id": 1,
        "device_token": "test_token_123",
        "device_model": "test_model",
        "status": 1
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 201
    assert response.json()["device_token"] == "test_token_123"
    assert response.json()["device_model"] == "test_model"
    assert response.json()["status"] == 1

def test_get_devices(auth_token):
    """测试获取设备列表"""
    # 创建设备
    client.post("/api/v1/devices/", json={
        "user_id": 1,
        "device_token": "test_token_123",
        "device_model": "test_model",
        "status": 1
    }, headers={"Authorization": f"Bearer {auth_token}"})
    
    # 获取设备列表
    response = client.get("/api/v1/devices/?user_id=1", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["device_token"] == "test_token_123"

def test_get_device_by_id(auth_token):
    """测试根据ID获取设备"""
    # 创建设备
    create_response = client.post("/api/v1/devices/", json={
        "user_id": 1,
        "device_token": "test_token_123",
        "device_model": "test_model",
        "status": 1
    }, headers={"Authorization": f"Bearer {auth_token}"})
    device_id = create_response.json()["device_id"]
    
    # 根据ID获取设备
    response = client.get(f"/api/v1/devices/{device_id}", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    assert response.json()["device_id"] == device_id
    assert response.json()["device_token"] == "test_token_123"

def test_update_device(auth_token):
    """测试更新设备"""
    # 创建设备
    create_response = client.post("/api/v1/devices/", json={
        "user_id": 1,
        "device_token": "test_token_123",
        "device_model": "test_model",
        "status": 1
    }, headers={"Authorization": f"Bearer {auth_token}"})
    device_id = create_response.json()["device_id"]
    
    # 更新设备
    response = client.put(f"/api/v1/devices/{device_id}", json={
        "device_model": "updated_model",
        "status": 0
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    assert response.json()["device_model"] == "updated_model"
    assert response.json()["status"] == 0

def test_delete_device(auth_token):
    """测试删除设备"""
    # 创建设备
    create_response = client.post("/api/v1/devices/", json={
        "user_id": 1,
        "device_token": "test_token_123",
        "device_model": "test_model",
        "status": 1
    }, headers={"Authorization": f"Bearer {auth_token}"})
    device_id = create_response.json()["device_id"]
    
    # 删除设备
    response = client.delete(f"/api/v1/devices/{device_id}", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 204
    
    # 验证设备已删除
    response = client.get(f"/api/v1/devices/{device_id}", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 404
