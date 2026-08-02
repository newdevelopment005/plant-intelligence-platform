from datetime import UTC, date, datetime

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.modules.project.domain.interfaces import (
    ProjectMemberRepositoryInterface,
    ProjectRepositoryInterface,
)
from app.modules.project.domain.models import ProjectMemberModel, ProjectModel


class CreateProjectUseCase:
    def __init__(
        self,
        project_repo: ProjectRepositoryInterface,
        member_repo: ProjectMemberRepositoryInterface,
    ):
        self.project_repo = project_repo
        self.member_repo = member_repo

    async def execute(
        self,
        name: str,
        owner_id: str,
        description: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        tags: list[str] | None = None,
    ) -> ProjectModel:
        self._validate_name(name)

        if start_date and end_date and end_date < start_date:
            raise ValidationException("End date must be after start date")

        project = ProjectModel(
            name=name.strip(),
            description=description.strip() if description else None,
            owner_id=owner_id,
            status="active",
            start_date=start_date,
            end_date=end_date,
            tags=tags,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        created = await self.project_repo.create(project)

        owner_member = ProjectMemberModel(
            project_id=created.id,
            user_id=owner_id,
            role="owner",
            joined_at=datetime.now(UTC),
        )
        await self.member_repo.add_member(owner_member)

        return created

    def _validate_name(self, name: str) -> None:
        if not name or not name.strip():
            raise ValidationException("Project name is required")
        if len(name.strip()) < 3:
            raise ValidationException("Project name must be at least 3 characters")
        if len(name.strip()) > 255:
            raise ValidationException("Project name must be less than 255 characters")


class ListProjectsUseCase:
    def __init__(
        self,
        project_repo: ProjectRepositoryInterface,
        member_repo: ProjectMemberRepositoryInterface,
    ):
        self.project_repo = project_repo
        self.member_repo = member_repo

    async def execute(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        status: str | None = None,
        search: str | None = None,
    ) -> dict:
        if search:
            projects = await self.project_repo.search(
                query=search, user_id=user_id, skip=skip, limit=limit
            )
            total = len(projects)
        else:
            projects = await self.project_repo.list_by_member(
                user_id=user_id, skip=skip, limit=limit
            )
            total = await self.project_repo.count_by_member(user_id)

        result = []
        for project in projects:
            member_count = await self.member_repo.count_members(str(project.id))
            result.append(
                {
                    "id": str(project.id),
                    "name": project.name,
                    "description": project.description,
                    "status": project.status,
                    "owner_id": str(project.owner_id),
                    "start_date": project.start_date.isoformat() if project.start_date else None,
                    "end_date": project.end_date.isoformat() if project.end_date else None,
                    "tags": project.tags,
                    "member_count": member_count,
                    "created_at": project.created_at.isoformat(),
                    "updated_at": project.updated_at.isoformat(),
                }
            )

        return {
            "items": result,
            "total": total,
            "skip": skip,
            "limit": limit,
        }


class GetProjectUseCase:
    def __init__(
        self,
        project_repo: ProjectRepositoryInterface,
        member_repo: ProjectMemberRepositoryInterface,
    ):
        self.project_repo = project_repo
        self.member_repo = member_repo

    async def execute(
        self, project_id: str, user_id: str
    ) -> dict:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException("Project", project_id)

        membership = await self.member_repo.get_by_project_and_user(
            project_id, user_id
        )
        if not membership:
            raise ValidationException("You are not a member of this project")

        members = await self.member_repo.list_members(project_id)
        member_list = []
        for m in members:
            member_list.append(
                {
                    "id": str(m.id),
                    "user_id": str(m.user_id),
                    "role": m.role,
                    "joined_at": m.joined_at.isoformat(),
                }
            )

        return {
            "id": str(project.id),
            "name": project.name,
            "description": project.description,
            "status": project.status,
            "owner_id": str(project.owner_id),
            "start_date": project.start_date.isoformat() if project.start_date else None,
            "end_date": project.end_date.isoformat() if project.end_date else None,
            "tags": project.tags,
            "metadata": project.metadata_json,
            "members": member_list,
            "member_count": len(member_list),
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat(),
        }


class UpdateProjectUseCase:
    def __init__(
        self,
        project_repo: ProjectRepositoryInterface,
        member_repo: ProjectMemberRepositoryInterface,
    ):
        self.project_repo = project_repo
        self.member_repo = member_repo

    async def execute(
        self,
        project_id: str,
        user_id: str,
        name: str | None = None,
        description: str | None = None,
        status: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        tags: list[str] | None = None,
    ) -> ProjectModel:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException("Project", project_id)

        membership = await self.member_repo.get_by_project_and_user(
            project_id, user_id
        )
        if not membership or membership.role not in ("owner", "admin"):
            raise ValidationException("Only owners and admins can update projects")

        if name is not None:
            if len(name.strip()) < 3:
                raise ValidationException("Project name must be at least 3 characters")
            project.name = name.strip()
        if description is not None:
            project.description = description.strip() if description else None
        if status is not None:
            if status not in ("active", "archived", "deleted"):
                raise ValidationException("Invalid status")
            project.status = status
        if start_date is not None:
            project.start_date = start_date
        if end_date is not None:
            project.end_date = end_date
        if tags is not None:
            project.tags = tags

        project.updated_at = datetime.now(UTC)
        return await self.project_repo.update(project)


class DeleteProjectUseCase:
    def __init__(
        self,
        project_repo: ProjectRepositoryInterface,
        member_repo: ProjectMemberRepositoryInterface,
    ):
        self.project_repo = project_repo
        self.member_repo = member_repo

    async def execute(self, project_id: str, user_id: str) -> dict:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException("Project", project_id)

        membership = await self.member_repo.get_by_project_and_user(
            project_id, user_id
        )
        if not membership or membership.role != "owner":
            raise ValidationException("Only the owner can delete a project")

        await self.project_repo.delete(project_id)
        return {"message": "Project deleted successfully"}


class AddMemberUseCase:
    def __init__(
        self,
        project_repo: ProjectRepositoryInterface,
        member_repo: ProjectMemberRepositoryInterface,
    ):
        self.project_repo = project_repo
        self.member_repo = member_repo

    async def execute(
        self, project_id: str, user_id: str, new_user_id: str, role: str = "member"
    ) -> ProjectMemberModel:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException("Project", project_id)

        requester_membership = await self.member_repo.get_by_project_and_user(
            project_id, user_id
        )
        if not requester_membership or requester_membership.role not in (
            "owner",
            "admin",
        ):
            raise ValidationException("Only owners and admins can add members")

        existing = await self.member_repo.get_by_project_and_user(
            project_id, new_user_id
        )
        if existing:
            raise ConflictException("User is already a member of this project")

        if role not in ("admin", "member", "readonly"):
            raise ValidationException("Invalid role")

        member = ProjectMemberModel(
            project_id=project_id,
            user_id=new_user_id,
            role=role,
            joined_at=datetime.now(UTC),
        )
        return await self.member_repo.add_member(member)


class RemoveMemberUseCase:
    def __init__(
        self,
        project_repo: ProjectRepositoryInterface,
        member_repo: ProjectMemberRepositoryInterface,
    ):
        self.project_repo = project_repo
        self.member_repo = member_repo

    async def execute(
        self, project_id: str, user_id: str, target_user_id: str
    ) -> dict:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException("Project", project_id)

        requester_membership = await self.member_repo.get_by_project_and_user(
            project_id, user_id
        )
        if not requester_membership or requester_membership.role not in (
            "owner",
            "admin",
        ):
            raise ValidationException("Only owners and admins can remove members")

        target_membership = await self.member_repo.get_by_project_and_user(
            project_id, target_user_id
        )
        if not target_membership:
            raise NotFoundException("Member", target_user_id)

        if target_membership.role == "owner":
            raise ValidationException("Cannot remove the project owner")

        await self.member_repo.remove_member(project_id, target_user_id)
        return {"message": "Member removed successfully"}


class UpdateMemberRoleUseCase:
    def __init__(
        self,
        project_repo: ProjectRepositoryInterface,
        member_repo: ProjectMemberRepositoryInterface,
    ):
        self.project_repo = project_repo
        self.member_repo = member_repo

    async def execute(
        self, project_id: str, user_id: str, target_user_id: str, new_role: str
    ) -> ProjectMemberModel:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException("Project", project_id)

        requester_membership = await self.member_repo.get_by_project_and_user(
            project_id, user_id
        )
        if not requester_membership or requester_membership.role != "owner":
            raise ValidationException("Only the owner can change member roles")

        target_membership = await self.member_repo.get_by_project_and_user(
            project_id, target_user_id
        )
        if not target_membership:
            raise NotFoundException("Member", target_user_id)

        if target_membership.role == "owner":
            raise ValidationException("Cannot change the owner's role")

        if new_role not in ("admin", "member", "readonly"):
            raise ValidationException("Invalid role")

        return await self.member_repo.update_member_role(
            project_id, target_user_id, new_role
        )
