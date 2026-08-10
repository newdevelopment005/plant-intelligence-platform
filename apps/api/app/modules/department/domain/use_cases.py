from datetime import UTC, datetime

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.modules.department.domain.interfaces import (
    DepartmentMemberRepositoryInterface,
    DepartmentRepositoryInterface,
)
from app.modules.department.domain.models import DepartmentMemberModel, DepartmentModel

VALID_MEMBER_ROLES = ("head", "member")


class ListDepartmentsUseCase:
    def __init__(
        self,
        department_repo: DepartmentRepositoryInterface,
        member_repo: DepartmentMemberRepositoryInterface,
    ):
        self.department_repo = department_repo
        self.member_repo = member_repo

    async def execute(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> dict:
        departments = await self.department_repo.list_all(
            skip=skip, limit=limit, search=search
        )
        total = await self.department_repo.count_all(search=search)

        items = []
        for dep in departments:
            members = await self.member_repo.list_members(str(dep.id))
            items.append(
                {
                    "id": str(dep.id),
                    "name": dep.name,
                    "code": dep.code,
                    "description": dep.description,
                    "head_user_id": str(dep.head_user_id) if dep.head_user_id else None,
                    "is_active": bool(dep.is_active),
                    "member_count": len(members),
                    "created_at": dep.created_at.isoformat(),
                    "updated_at": dep.updated_at.isoformat(),
                }
            )

        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
        }


class CreateDepartmentUseCase:
    def __init__(
        self,
        department_repo: DepartmentRepositoryInterface,
        member_repo: DepartmentMemberRepositoryInterface,
    ):
        self.department_repo = department_repo
        self.member_repo = member_repo

    async def execute(
        self,
        name: str,
        created_by: str,
        code: str | None = None,
        description: str | None = None,
        head_user_id: str | None = None,
    ) -> DepartmentModel:
        self._validate_name(name)
        if code and len(code.strip()) > 50:
            raise ValidationException("Department code must be less than 50 characters")

        department = DepartmentModel(
            name=name.strip(),
            code=code.strip().upper() if code and code.strip() else None,
            description=description.strip() if description else None,
            head_user_id=head_user_id,
            created_by=created_by,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        created = await self.department_repo.create(department)

        if head_user_id:
            member = DepartmentMemberModel(
                department_id=created.id,
                user_id=head_user_id,
                role="head",
                joined_at=datetime.now(UTC),
            )
            await self.member_repo.add_member(member)

        return created

    def _validate_name(self, name: str) -> None:
        if not name or not name.strip():
            raise ValidationException("Department name is required")
        if len(name.strip()) < 2:
            raise ValidationException("Department name must be at least 2 characters")
        if len(name.strip()) > 255:
            raise ValidationException("Department name must be less than 255 characters")


class UpdateDepartmentUseCase:
    def __init__(
        self,
        department_repo: DepartmentRepositoryInterface,
        member_repo: DepartmentMemberRepositoryInterface,
    ):
        self.department_repo = department_repo
        self.member_repo = member_repo

    async def execute(
        self,
        department_id: str,
        name: str | None = None,
        code: str | None = None,
        description: str | None = None,
        head_user_id: str | None = None,
        is_active: bool | None = None,
    ) -> DepartmentModel:
        department = await self.department_repo.get_by_id(department_id)
        if not department:
            raise NotFoundException("Department", department_id)

        if name is not None:
            self._validate_name(name)
            department.name = name.strip()

        if code is not None:
            department.code = code.strip().upper() if code.strip() else None

        if description is not None:
            department.description = description.strip() if description.strip() else None

        if is_active is not None:
            department.is_active = is_active

        if head_user_id is not None:
            department.head_user_id = head_user_id or None
            current_head = await self.member_repo.get_by_department_and_user(
                department_id, head_user_id
            ) if head_user_id else None
            if not current_head and head_user_id:
                member = DepartmentMemberModel(
                    department_id=department_id,
                    user_id=head_user_id,
                    role="head",
                    joined_at=datetime.now(UTC),
                )
                await self.member_repo.add_member(member)

        return await self.department_repo.update(department)

    def _validate_name(self, name: str) -> None:
        if not name or not name.strip():
            raise ValidationException("Department name is required")
        if len(name.strip()) < 2:
            raise ValidationException("Department name must be at least 2 characters")
        if len(name.strip()) > 255:
            raise ValidationException("Department name must be less than 255 characters")


class DeleteDepartmentUseCase:
    def __init__(
        self,
        department_repo: DepartmentRepositoryInterface,
        member_repo: DepartmentMemberRepositoryInterface,
    ):
        self.department_repo = department_repo
        self.member_repo = member_repo

    async def execute(self, department_id: str) -> dict:
        department = await self.department_repo.get_by_id(department_id)
        if not department:
            raise NotFoundException("Department", department_id)
        await self.department_repo.delete(department_id)
        return {"message": "Department deleted successfully"}


class AddDepartmentMemberUseCase:
    def __init__(
        self,
        department_repo: DepartmentRepositoryInterface,
        member_repo: DepartmentMemberRepositoryInterface,
    ):
        self.department_repo = department_repo
        self.member_repo = member_repo

    async def execute(
        self, department_id: str, target_user_id: str, role: str = "member"
    ) -> DepartmentMemberModel:
        department = await self.department_repo.get_by_id(department_id)
        if not department:
            raise NotFoundException("Department", department_id)

        existing = await self.member_repo.get_by_department_and_user(
            department_id, target_user_id
        )
        if existing:
            raise ConflictException("User is already a member of this department")

        if role not in VALID_MEMBER_ROLES:
            raise ValidationException(
                f"Invalid role. Must be one of: {', '.join(VALID_MEMBER_ROLES)}"
            )

        member = DepartmentMemberModel(
            department_id=department_id,
            user_id=target_user_id,
            role=role,
            joined_at=datetime.now(UTC),
        )
        return await self.member_repo.add_member(member)


class UpdateDepartmentMemberRoleUseCase:
    def __init__(
        self,
        department_repo: DepartmentRepositoryInterface,
        member_repo: DepartmentMemberRepositoryInterface,
    ):
        self.department_repo = department_repo
        self.member_repo = member_repo

    async def execute(
        self, department_id: str, target_user_id: str, role: str
    ) -> DepartmentMemberModel:
        department = await self.department_repo.get_by_id(department_id)
        if not department:
            raise NotFoundException("Department", department_id)

        if role not in VALID_MEMBER_ROLES:
            raise ValidationException(
                f"Invalid role. Must be one of: {', '.join(VALID_MEMBER_ROLES)}"
            )

        member = await self.member_repo.update_role(
            department_id, target_user_id, role
        )
        if not member:
            raise NotFoundException("Member", target_user_id)
        return member


class RemoveDepartmentMemberUseCase:
    def __init__(
        self,
        department_repo: DepartmentRepositoryInterface,
        member_repo: DepartmentMemberRepositoryInterface,
    ):
        self.department_repo = department_repo
        self.member_repo = member_repo

    async def execute(self, department_id: str, target_user_id: str) -> dict:
        department = await self.department_repo.get_by_id(department_id)
        if not department:
            raise NotFoundException("Department", department_id)

        removed = await self.member_repo.remove_member(department_id, target_user_id)
        if not removed:
            raise NotFoundException("Member", target_user_id)

        if str(department.head_user_id) == target_user_id:
            department.head_user_id = None
            await self.department_repo.update(department)

        return {"message": "Member removed successfully"}