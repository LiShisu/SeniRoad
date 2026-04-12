from httpx import AsyncClient
from app.config import settings
import json
from typing import Dict, List, Optional

class NavigationService:
    def __init__(self):
        self.client = AsyncClient()
        self.amap_key = settings.AMAP_API_KEY
        self.base_url = "https://restapi.amap.com/v3"
    
    async def plan_route(self, origin: str, destination: str, priority: str = "elderly_friendly"):
        """规划导航路线
        
        Args:
            origin: 起点坐标，格式为"经度,纬度"
            destination: 终点坐标，格式为"经度,纬度"或目的地名称
            priority: 优先级，可选值为"elderly_friendly"（默认）、"time"、"distance"
            
        Returns:
            Dict: 包含路线信息的字典
        """
        # 构建请求参数
        params = {
            "origin": origin,
            "destination": destination,
            "key": self.amap_key,
            "extensions": "all"
        }
        
        # 发送请求获取路线数据
        response = await self.client.get(f"{self.base_url}/direction/walking", params=params)
        route_data = response.json()
        
        # 根据优先级过滤路线
        if priority == "elderly_friendly":
            route_data = self._filter_elderly_friendly(route_data)
        elif priority == "time":
            route_data = self._filter_fastest_route(route_data)
        elif priority == "distance":
            route_data = self._filter_shortest_route(route_data)
        
        return route_data
    
    def _filter_elderly_friendly(self, route_data: dict) -> dict:
        """过滤出老年人友好的路线
        
        考虑因素：
        - 阶梯数量少
        - 遮阳设施充足
        - 路面平整度高
        - 休息区域多
        
        Args:
            route_data: 原始路线数据
            
        Returns:
            Dict: 过滤后的路线数据
        """
        if "route" not in route_data:
            return route_data
        
        route = route_data["route"]
        if "paths" not in route:
            return route_data
        
        paths = route["paths"]
        if not paths:
            return route_data
        
        # 计算每条路径的老年人友好度得分
        best_path = None
        best_score = -1
        
        for path in paths:
            score = self._calculate_elderly_friendly_score(path)
            if score > best_score:
                best_score = score
                best_path = path
        
        # 只保留最优路径
        route["paths"] = [best_path] if best_path else []
        route_data["route"] = route
        
        return route_data
    
    def _calculate_elderly_friendly_score(self, path: dict) -> float:
        """计算路径的老年人友好度得分
        
        Args:
            path: 路径数据
            
        Returns:
            float: 友好度得分，越高越友好
        """
        score = 0.0
        
        # 基础得分
        score += 100.0
        
        # 距离因素：距离越短得分越高
        distance = path.get("distance", 0)
        distance = float(distance) if distance else 0
        score -= distance / 100  # 每100米减1分
        
        # 时间因素：时间越短得分越高
        duration = path.get("duration", 0)
        duration = float(duration) if duration else 0
        score -= duration / 60  # 每分钟减1分
        
        # 步数因素：步数越少得分越高
        steps = path.get("steps", [])
        step_count = len(steps)
        score -= step_count * 0.5  # 每步减0.5分
        
        # 阶梯因素：假设包含"阶梯"的步骤会减少得分
        for step in steps:
            instruction = step.get("instruction", "")
            if "阶梯" in instruction:
                score -= 10.0  # 每个阶梯步骤减10分
            if "上坡" in instruction:
                score -= 5.0  # 每个上坡步骤减5分
            if "下坡" in instruction:
                score -= 3.0  # 每个下坡步骤减3分
        
        return max(0, score)  # 确保得分不为负
    
    def _filter_fastest_route(self, route_data: dict) -> dict:
        """过滤出最快的路线
        
        Args:
            route_data: 原始路线数据
            
        Returns:
            Dict: 过滤后的路线数据
        """
        if "route" not in route_data:
            return route_data
        
        route = route_data["route"]
        if "paths" not in route:
            return route_data
        
        paths = route["paths"]
        if not paths:
            return route_data
        
        # 找出时间最短的路径
        fastest_path = None
        min_duration = float('inf')
        
        for path in paths:
            duration = path.get("duration", 0)
            duration = float(duration) if duration else 0
            if duration < min_duration:
                min_duration = duration
                fastest_path = path
        
        # 只保留最快路径
        route["paths"] = [fastest_path] if fastest_path else []
        route_data["route"] = route
        
        return route_data
    
    def _filter_shortest_route(self, route_data: dict) -> dict:
        """过滤出最短的路线
        
        Args:
            route_data: 原始路线数据
            
        Returns:
            Dict: 过滤后的路线数据
        """
        if "route" not in route_data:
            return route_data
        
        route = route_data["route"]
        if "paths" not in route:
            return route_data
        
        paths = route["paths"]
        if not paths:
            return route_data
        
        # 找出距离最短的路径
        shortest_path = None
        min_distance = float('inf')
        
        for path in paths:
            distance = path.get("distance", 0)
            distance = float(distance) if distance else 0
            if distance < min_distance:
                min_distance = distance
                shortest_path = path
        
        # 只保留最短路径
        route["paths"] = [shortest_path] if shortest_path else []
        route_data["route"] = route
        
        return route_data
