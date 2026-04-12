from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.models import User
from sqlalchemy.orm import Session
import pytest
from unittest.mock import patch

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

@patch('app.services.auth.hash_password')
@patch('app.services.auth.verify_password')
def test_register(mock_verify, mock_hash, db_session):
    """测试用户注册"""
    mock_hash.return_value = "hashed_password"
    
    response = client.post("/api/v1/auth/register", json={
        "phone": "13800138000",
        "password": "123456",
        "nickname": "测试用户",
        "role": "elderly"
    })
    assert response.status_code == 201
    assert response.json()["phone"] == "13800138000"
    assert response.json()["nickname"] == "测试用户"
    assert response.json()["role"] == "elderly"

@patch('app.services.auth.hash_password')
@patch('app.services.auth.verify_password')
def test_login(mock_verify, mock_hash, db_session):
    """测试用户登录"""
    mock_hash.return_value = "hashed_password"
    mock_verify.return_value = True
    
    # 先注册用户
    client.post("/api/v1/auth/register", json={
        "phone": "13800138000",
        "password": "123456",
        "nickname": "测试用户",
        "role": "elderly"
    })
    
    # 登录
    response = client.post("/api/v1/auth/login", data={
        "username": "13800138000",
        "password": "123456"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

@patch('app.services.auth.verify_password')
def test_login_invalid_credentials(mock_verify, db_session):
    """测试登录失败（无效凭证）"""
    mock_verify.return_value = False
    
    response = client.post("/api/v1/auth/login", data={
        "username": "13800138000",
        "password": "wrong"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect phone or password"
