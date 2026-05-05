import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_sse_navigation():
    """测试 SSE 流式导航接口"""
    print("=== 测试 SSE 流式导航接口 ===")

    origin_lng = "117.11398861958695"
    origin_lat = "36.651626279380984"
    favorite_place_id = 3

    print(f"\n测试参数:")
    print(f"  - 起点经度: {origin_lng}")
    print(f"  - 起点纬度: {origin_lat}")
    print(f"  - 收藏地点ID: {favorite_place_id}")

    request_data = {
        "favorite_place_id": favorite_place_id,
        "origin_lng": origin_lng,
        "origin_lat": origin_lat
    }

    try:
        with requests.post(
            f"{BASE_URL}/navigation/plan-stream",
            json=request_data,
            stream=True,
            headers={"Accept": "text/event-stream"}
        ) as response:
            print(f"\n请求状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("\n收到 SSE 事件流:")
                print("-" * 60)
                
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        if line.startswith("event:"):
                            event_type = line.replace("event:", "").strip()
                            print(f"\n【事件类型】: {event_type}")
                        elif line.startswith("data:"):
                            data = line.replace("data:", "").strip()
                            try:
                                parsed = json.loads(data)
                                print(f"【数据】: {json.dumps(parsed, ensure_ascii=False, indent=2)}")
                            except:
                                print(f"【数据】: {data}")
                    else:
                        print("-" * 60)
            else:
                print(f"响应: {response.text}")
                
    except Exception as e:
        print(f"\n请求失败: {e}")

def test_original_navigation():
    """测试原始导航接口"""
    print("\n\n=== 测试原始导航接口 ===")
    
    origin_lng = "117.11398861958695"
    origin_lat = "36.651626279380984"
    favorite_place_id = 3
    
    request_data = {
        "favorite_place_id": favorite_place_id,
        "origin_lng": origin_lng,
        "origin_lat": origin_lat
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/navigation/plan",
            json=request_data,
            timeout=60
        )
        print(f"\n请求状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except requests.exceptions.Timeout:
        print("\n请求超时 (60秒)")
    except Exception as e:
        print(f"\n请求失败: {e}")

if __name__ == "__main__":
    print("SSE 接口测试脚本")
    print("=" * 60)
    test_sse_navigation()
    test_original_navigation()
