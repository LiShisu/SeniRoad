import requests
import json

BASE_URL = "http://localhost:8000/api/v1/llm-navigation-agent"

def test_process_text():
    """测试 process-text 接口"""
    print("=== 测试 process-text 接口 ===")
    
    # 测试用例 1: 基本测试 - 只提供文本
    print("\n测试用例 1: 只提供文本")
    params = {
        "text": "我要去天安门"
    }
    response = requests.post(f"{BASE_URL}/process-text", params=params)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
    try:
        print(f"JSON响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except:
        pass
    
    # 测试用例 2: 提供文本和当前位置
    print("\n测试用例 2: 提供文本和当前位置")
    params = {
        "text": "我要去天安门",
        "current_location": "116.397428,39.90923"
    }
    response = requests.post(f"{BASE_URL}/process-text", params=params)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
    try:
        print(f"JSON响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except:
        pass
    
    # 测试用例 3: 测试不同的目的地
    print("\n测试用例 3: 测试不同的目的地")
    destinations = ["北京西站", "颐和园", "北京大学"]
    for dest in destinations:
        params = {
            "text": f"我要去{dest}",
            "current_location": "116.397428,39.90923"
        }
        response = requests.post(f"{BASE_URL}/process-text", params=params)
        print(f"目的地: {dest}")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        try:
            print(f"JSON响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        except:
            pass
        print("-" * 50)

if __name__ == "__main__":
    test_process_text()