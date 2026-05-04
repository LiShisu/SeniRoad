from app.models.binding import Binding, BindingStatus
from app.models.user import UserRole
from app.schemas.binding import BindingCreate, BindingResponse, BindingUnbind
from app.repositories.binding_repository import BindingRepository
from app.repositories.user_repository import UserRepository
from typing import List, Optional
from datetime import datetime


class BindingService:
    def __init__(self, binding_repo: BindingRepository, user_repo: UserRepository):
        self.binding_repo = binding_repo
        self.user_repo = user_repo

    def get_binding_by_id(self, binding_id: int) -> Optional[BindingResponse]:
        binding = self.binding_repo.get_by_id(binding_id)
        if binding:
            response = BindingResponse.model_validate(binding)
            if binding.elderly:
                response.elderly_nickname = binding.elderly.nickname
                response.elderly_phone = binding.elderly.phone
            if binding.family:
                response.family_phone = binding.family.phone
                response.family_nickname = binding.family.nickname
            return response
        return None

    def get_bindings_for_user(self, user_id: int, user_role: UserRole) -> List[BindingResponse]:
        if user_role == UserRole.ELDERLY:
            bindings = self.binding_repo.get_by_elderly_id(user_id)
        else:
            bindings = self.binding_repo.get_by_family_id(user_id)

        responses = []
        for binding in bindings:
            response = BindingResponse.model_validate(binding)
            if binding.elderly:
                response.elderly_nickname = binding.elderly.nickname
                response.elderly_phone = binding.elderly.phone
            if binding.family:
                response.family_phone = binding.family.phone
                response.family_nickname = binding.family.nickname
            responses.append(response)
        return responses

    def create_binding(self, binding_data: BindingCreate) -> BindingResponse:
        elderly_user = self.user_repo.get_by_phone(binding_data.elderly_phone)
        if not elderly_user:
            raise ValueError("未找到该手机号对应的老人用户")
        if elderly_user.role != UserRole.ELDERLY:
            raise ValueError("该手机号对应的用户不是老人用户")

        existing_binding = self.binding_repo.get_binding_by_elderly_and_family(
            elderly_user.user_id,
            binding_data.family_id
        )
        if existing_binding:
            raise ValueError("绑定关系已存在")

        binding = Binding(
            elderly_id=elderly_user.user_id,
            family_id=binding_data.family_id,
            status=BindingStatus.ACCEPTED # TODO: 后续改成待审核状态
        )
        created_binding = self.binding_repo.create(binding)
        response = BindingResponse.model_validate(created_binding)
        response.elderly_nickname = elderly_user.nickname
        response.elderly_phone = elderly_user.phone
        family_user = self.user_repo.get_by_id(binding_data.family_id)
        if family_user:
            response.family_phone = family_user.phone
            response.family_nickname = family_user.nickname
        return response

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
