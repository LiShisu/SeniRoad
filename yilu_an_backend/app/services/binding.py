from app.models.binding import Binding, BindingStatus
from app.models.user import UserRole
from app.schemas.binding import BindingCreate, BindingResponse, BindingUnbind,BindingUser
from app.repositories.binding_repository import BindingRepository
from app.repositories.user_repository import UserRepository
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException, status
from app.schemas.exception import NotFoundException, ForbiddenException,BusinessException
class BindingService:
    def __init__(self, binding_repo: BindingRepository, user_repo: UserRepository):
        self.binding_repo = binding_repo
        self.user_repo = user_repo

    # 辅助方法：将数据库对象转化为嵌套的 Resource Representation
    def _build_response(self, binding: Binding) -> BindingResponse:
        response = BindingResponse.model_validate(binding)
        if binding.elderly:
            response.elderly = BindingUser.model_validate(binding.elderly)
        if binding.family:
            response.family = BindingUser.model_validate(binding.family)
        return response

    # def get_binding_by_id(self, binding_id: int) -> Optional[BindingResponse]:
    #     binding = self.binding_repo.get_by_id(binding_id)
    #     if binding:
    #         response = BindingResponse.model_validate(binding)
    #         if binding.elderly:
    #             response.elderly_nickname = binding.elderly.nickname
    #             response.elderly_phone = binding.elderly.phone
    #         if binding.family:
    #             response.family_phone = binding.family.phone
    #             response.family_nickname = binding.family.nickname
    #         return response
    #     return None

    def get_bindings_for_user(self, user_id: int, user_role: UserRole) -> List[BindingResponse]:
        if user_role == UserRole.ELDERLY:
            bindings = self.binding_repo.get_by_elderly_id(user_id)
        else:
            bindings = self.binding_repo.get_by_family_id(user_id)
        return [self._build_response(b) for b in bindings]
        # responses = []
        # for binding in bindings:
        #     response = BindingResponse.model_validate(binding)
        #     if binding.elderly:
        #         response.elderly_nickname = binding.elderly.nickname
        #         response.elderly_phone = binding.elderly.phone
        #     if binding.family:
        #         response.family_phone = binding.family.phone
        #         response.family_nickname = binding.family.nickname
        #     responses.append(response)
        # return responses

    # def create_binding(self, binding_data: BindingCreate) -> BindingResponse:
    #     elderly_user = self.user_repo.get_by_phone(binding_data.elderly_phone)
    #     if not elderly_user:
    #         raise ValueError("未找到该手机号对应的老人用户")
    #     if elderly_user.role != UserRole.ELDERLY:
    #         raise ValueError("该手机号对应的用户不是老人用户")

    #     existing_binding = self.binding_repo.get_binding_by_elderly_and_family(
    #         elderly_user.user_id,
    #         binding_data.family_id
    #     )
    #     if existing_binding:
    #         raise ValueError("绑定关系已存在")

    #     binding = Binding(
    #         elderly_id=elderly_user.user_id,
    #         family_id=binding_data.family_id,
    #         status=BindingStatus.ACCEPTED # TODO: 后续改成待审核状态
    #     )
    #     created_binding = self.binding_repo.create(binding)
    #     response = BindingResponse.model_validate(created_binding)
    #     response.elderly_nickname = elderly_user.nickname
    #     response.elderly_phone = elderly_user.phone
    #     family_user = self.user_repo.get_by_id(binding_data.family_id)
    #     if family_user:
    #         response.family_phone = family_user.phone
    #         response.family_nickname = family_user.nickname
    #     return response
    def create_binding(self, elderly_phone: str, family_id: int) -> BindingResponse:
        elderly_user = self.user_repo.get_by_phone(elderly_phone)
        if not elderly_user:
            raise HTTPException(status_code=404, detail="未找到该手机号对应的老人用户")
        if elderly_user.role != UserRole.ELDERLY:
            raise HTTPException(status_code=400, detail="该手机号不是老人账号，无法绑定")

        existing_binding = self.binding_repo.get_binding_by_elderly_and_family(elderly_user.user_id, family_id)
        if existing_binding:
            raise HTTPException(status_code=400, detail="绑定关系已存在或正在审核中")

        # 修复：创建时状态应当是 PENDING
        binding = Binding(
            elderly_id=elderly_user.user_id,
            family_id=family_id,
            status=BindingStatus.ACCEPTED #直接同意了
        )
        created_binding = self.binding_repo.create(binding)
        
        # 强制加载关联用户数据以便生成完整表述
        created_binding.elderly = elderly_user
        created_binding.family = self.user_repo.get_by_id(family_id)
        
        return self._build_response(created_binding)

    # TODO:解绑、拒绝绑定、批准绑定待采用
    def unbind(self, unbind_data: BindingUnbind) -> None:
        elderly_user = self.user_repo.get_by_phone(unbind_data.elderly_phone)
        if not elderly_user:
            raise ValueError("未找到该手机号对应的老人用户")

        binding = self.binding_repo.get_binding_by_elderly_and_family(
            elderly_user.user_id,
            unbind_data.family_id
        )
        if not binding:
            raise ValueError("绑定关系不存在")

        self.binding_repo.delete(binding)

    def approve_binding(self, binding_id: int, user_id: int) -> BindingResponse:
        binding = self.binding_repo.get_by_id(binding_id)
        if not binding:
            raise ValueError("绑定关系不存在")

        if binding.elderly_id != user_id:
            raise PermissionError("只有老人可以批准绑定请求")

        binding.status = BindingStatus.ACCEPTED
        updated_binding = self.binding_repo.update(binding)
        response = BindingResponse.model_validate(updated_binding)
        if binding.elderly:
            response.elderly_nickname = binding.elderly.nickname
            response.elderly_phone = binding.elderly.phone
        if binding.family:
            response.family_phone = binding.family.phone
            response.family_nickname = binding.family.nickname
        return response

    def reject_binding(self, binding_id: int, user_id: int) -> BindingResponse:
        binding = self.binding_repo.get_by_id(binding_id)
        if not binding:
            raise ValueError("绑定关系不存在")

        if binding.elderly_id != user_id:
            raise PermissionError("只有老人可以拒绝绑定请求")

        binding.status = BindingStatus.REJECTED
        updated_binding = self.binding_repo.update(binding)
        response = BindingResponse.model_validate(updated_binding)
        if binding.elderly:
            response.elderly_nickname = binding.elderly.nickname
            response.elderly_phone = binding.elderly.phone
        if binding.family:
            response.family_phone = binding.family.phone
            response.family_nickname = binding.family.nickname
        return response
    def update_binding_status(self, binding_id: int, target_status: BindingStatus, current_user_id: int) -> BindingResponse:
        """更新资源状态 (核心逻辑：状态机保护 + 时间戳记录)"""
        binding = self.binding_repo.get_by_id(binding_id)
        if not binding:
            raise NotFoundException("绑定关系不存在")
        # 权限校验
        if binding.elderly_id != current_user_id:
            raise ForbiddenException("只有老人可以操作此绑定请求")
        if binding.status != BindingStatus.PENDING:
             raise BusinessException(
                 message=f"该绑定请求已处理，当前状态为: {binding.status}，不可重复操作",
                 code=400
             )
        # 执行更新
        binding.status = target_status
        binding.approved_at = datetime.now() 
        updated_binding = self.binding_repo.update(binding)
        # 返回资源表述 (API 层会自动将其装入 Result 信封)
        return self._build_response(updated_binding)
    
    # def delete_binding(self, binding_id: int, current_user_id: int) -> None:
    #     binding = self.binding_repo.get_by_id(binding_id)
    #     if not binding:
    #         raise HTTPException(status_code=404, detail="绑定关系不存在")

    #     # 权限校验：双方都可以解除绑定
    #     if current_user_id not in [binding.elderly_id, binding.family_id]:
    #         raise HTTPException(status_code=403, detail="没有权限解除此绑定关系")

    #     self.binding_repo.delete(binding)
    def delete_binding(self, binding_id: int, current_user_id: int) -> None:
        """删除资源 (核心逻辑：权限隔离)"""
        binding = self.binding_repo.get_by_id(binding_id)
        if not binding:
            raise NotFoundException("绑定关系不存在")
        # 权限校验：双方均可发起解绑，这符合“老年人导航”项目中家属和老人对等的安全退出权利
        if current_user_id not in [binding.elderly_id, binding.family_id]:
            raise ForbiddenException("没有权限解除此绑定关系")
        self.binding_repo.delete(binding)