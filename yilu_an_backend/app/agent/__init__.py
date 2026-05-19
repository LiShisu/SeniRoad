"""
智能导航Agent模块

基于LangChain和LangGraph的多Agent协作系统：
- workflow: 新的导航工作流（推荐使用）
- multi_agent_navigation: 旧的多Agent导航服务（兼容）
"""

from app.agent.workflow import (
    create_navigation_graph,
    execute_navigation_workflow,
    execute_navigation_workflow_stream,
)
from app.agent.schemas import NavigationWorkflowState

__all__ = [
    "create_navigation_graph",
    "execute_navigation_workflow",
    "execute_navigation_workflow_stream",
    "NavigationWorkflowState",
]
