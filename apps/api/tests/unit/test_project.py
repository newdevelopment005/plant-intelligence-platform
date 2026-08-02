from datetime import UTC, datetime

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.modules.project.domain.interfaces import (
    ProjectMemberRepositoryInterface,
    ProjectRepositoryInterface,
)
from app.modules.project.domain.models import ProjectMemberModel, ProjectModel
from app.modules.project.domain.use_cases import (
    AddMemberUseCase,
    CreateProjectUseCase,
    DeleteProjectUseCase,
    GetProjectUseCase,
    ListProjectsUseCase,
    RemoveMemberUseCase,
    UpdateMemberRoleUseCase,
    UpdateProjectUseCase,
)


class TestCreateProjectUseCase:
    def setup_method(self):
        self.project_repo = MagicMock(spec=ProjectRepositoryInterface)
        self.member_repo = MagicMock(spec=ProjectMemberRepositoryInterface)
        self.use_case = CreateProjectUseCase(self.project_repo, self.member_repo)

    @pytest.mark.asyncio
    async def test_create_project_success(self):
        self.project_repo.get_by_name = AsyncMock(return_value=None)
        self.project_repo.create = AsyncMock(return_value=ProjectModel(
            id="proj-123", name="Drought Study", description="Testing drought resistance",
            status="active", owner_id="user-456", tags=["drought", "wheat"],
        ))
        self.member_repo.add_member = AsyncMock(return_value=ProjectMemberModel(
            id="mem-1", project_id="proj-123", user_id="user-456", role="owner",
        ))
        result = await self.use_case.execute(owner_id="user-456", name="Drought Study", description="Testing drought resistance", tags=["drought", "wheat"])
        assert result.name == "Drought Study"
        self.project_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_project_empty_name(self):
        with pytest.raises(ValidationException):
            await self.use_case.execute(owner_id="user-456", name="")

    @pytest.mark.asyncio
    async def test_create_project_whitespace_name(self):
        with pytest.raises(ValidationException):
            await self.use_case.execute(owner_id="user-456", name="   ")

    @pytest.mark.asyncio
    async def test_create_project_name_too_short(self):
        with pytest.raises(ValidationException):
            await self.use_case.execute(owner_id="user-456", name="AB")

    @pytest.mark.asyncio
    async def test_create_project_invalid_dates(self):
        from datetime import date
        with pytest.raises(ValidationException):
            await self.use_case.execute(owner_id="user-456", name="Valid Name", start_date=date(2025, 12, 31), end_date=date(2025, 1, 1))


class TestListProjectsUseCase:
    def setup_method(self):
        self.project_repo = MagicMock(spec=ProjectRepositoryInterface)
        self.member_repo = MagicMock(spec=ProjectMemberRepositoryInterface)
        self.use_case = ListProjectsUseCase(self.project_repo, self.member_repo)

    @pytest.mark.asyncio
    async def test_list_projects_success(self):
        self.project_repo.list_by_member = AsyncMock(return_value=[])
        self.project_repo.count_by_member = AsyncMock(return_value=0)
        result = await self.use_case.execute(user_id="user-1")
        assert result["items"] == []
        assert result["total"] == 0

    @pytest.mark.asyncio
    async def test_list_projects_with_search(self):
        self.project_repo.search = AsyncMock(return_value=[])
        self.member_repo.count_members = AsyncMock(return_value=0)
        result = await self.use_case.execute(user_id="user-1", search="drought")
        assert result["items"] == []


class TestGetProjectUseCase:
    def setup_method(self):
        self.project_repo = MagicMock(spec=ProjectRepositoryInterface)
        self.member_repo = MagicMock(spec=ProjectMemberRepositoryInterface)
        self.use_case = GetProjectUseCase(self.project_repo, self.member_repo)

    @pytest.mark.asyncio
    async def test_get_project_success(self):
        project = ProjectModel(id="proj-1", owner_id="user-1", name="Test", created_at=datetime.now(UTC), updated_at=datetime.now(UTC))
        member = ProjectMemberModel(id="mem-1", project_id="proj-1", user_id="user-1", role="owner", joined_at=datetime.now(UTC))
        self.project_repo.get_by_id = AsyncMock(return_value=project)
        self.member_repo.get_by_project_and_user = AsyncMock(return_value=member)
        self.member_repo.list_members = AsyncMock(return_value=[member])
        result = await self.use_case.execute(project_id="proj-1", user_id="user-1")
        assert result["id"] == "proj-1"

    @pytest.mark.asyncio
    async def test_get_project_not_found(self):
        self.project_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute(project_id="proj-999", user_id="user-1")

    @pytest.mark.asyncio
    async def test_get_project_not_member(self):
        project = ProjectModel(id="proj-1", owner_id="user-2", name="Test")
        self.project_repo.get_by_id = AsyncMock(return_value=project)
        self.member_repo.get_by_project_and_user = AsyncMock(return_value=None)
        with pytest.raises(ValidationException):
            await self.use_case.execute(project_id="proj-1", user_id="user-1")


class TestUpdateProjectUseCase:
    def setup_method(self):
        self.project_repo = MagicMock(spec=ProjectRepositoryInterface)
        self.member_repo = MagicMock(spec=ProjectMemberRepositoryInterface)
        self.use_case = UpdateProjectUseCase(self.project_repo, self.member_repo)

    @pytest.mark.asyncio
    async def test_update_project_success(self):
        project = ProjectModel(id="proj-1", owner_id="user-1", name="Test")
        member = ProjectMemberModel(id="mem-1", project_id="proj-1", user_id="user-1", role="owner", joined_at=datetime.now(UTC))
        self.project_repo.get_by_id = AsyncMock(return_value=project)
        self.member_repo.get_by_project_and_user = AsyncMock(return_value=member)
        self.project_repo.update = AsyncMock(return_value=project)
        result = await self.use_case.execute(project_id="proj-1", user_id="user-1", name="Updated Name")
        assert result.name == "Test" or result.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_update_project_not_found(self):
        self.project_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute(project_id="proj-999", user_id="user-1", name="X")

    @pytest.mark.asyncio
    async def test_update_project_forbidden(self):
        project = ProjectModel(id="proj-1", owner_id="user-2", name="Test")
        member = ProjectMemberModel(id="mem-1", project_id="proj-1", user_id="user-1", role="researcher", joined_at=datetime.now(UTC))
        self.project_repo.get_by_id = AsyncMock(return_value=project)
        self.member_repo.get_by_project_and_user = AsyncMock(return_value=member)
        with pytest.raises(ValidationException):
            await self.use_case.execute(project_id="proj-1", user_id="user-1", name="X")


class TestDeleteProjectUseCase:
    def setup_method(self):
        self.project_repo = MagicMock(spec=ProjectRepositoryInterface)
        self.member_repo = MagicMock(spec=ProjectMemberRepositoryInterface)
        self.use_case = DeleteProjectUseCase(self.project_repo, self.member_repo)

    @pytest.mark.asyncio
    async def test_delete_project_success(self):
        project = ProjectModel(id="proj-1", owner_id="user-1", name="Test")
        member = ProjectMemberModel(id="mem-1", project_id="proj-1", user_id="user-1", role="owner", joined_at=datetime.now(UTC))
        self.project_repo.get_by_id = AsyncMock(return_value=project)
        self.member_repo.get_by_project_and_user = AsyncMock(return_value=member)
        self.project_repo.delete = AsyncMock(return_value=True)
        result = await self.use_case.execute(project_id="proj-1", user_id="user-1")
        assert result is True or isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_delete_project_not_found(self):
        self.project_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute(project_id="proj-999", user_id="user-1")

    @pytest.mark.asyncio
    async def test_delete_project_forbidden(self):
        project = ProjectModel(id="proj-1", owner_id="user-2", name="Test")
        member = ProjectMemberModel(id="mem-1", project_id="proj-1", user_id="user-1", role="researcher", joined_at=datetime.now(UTC))
        self.project_repo.get_by_id = AsyncMock(return_value=project)
        self.member_repo.get_by_project_and_user = AsyncMock(return_value=member)
        with pytest.raises(ValidationException):
            await self.use_case.execute(project_id="proj-1", user_id="user-1")


class TestAddMemberUseCase:
    def setup_method(self):
        self.project_repo = MagicMock(spec=ProjectRepositoryInterface)
        self.member_repo = MagicMock(spec=ProjectMemberRepositoryInterface)
        self.use_case = AddMemberUseCase(self.project_repo, self.member_repo)

    @pytest.mark.asyncio
    async def test_add_member_success(self):
        project = ProjectModel(id="proj-1", owner_id="user-1", name="Test")
        owner_member = ProjectMemberModel(id="mem-1", project_id="proj-1", user_id="user-1", role="owner", joined_at=datetime.now(UTC))
        new_member = ProjectMemberModel(id="mem-2", project_id="proj-1", user_id="user-2", role="member", joined_at=datetime.now(UTC))
        self.project_repo.get_by_id = AsyncMock(return_value=project)
        self.member_repo.get_by_project_and_user = AsyncMock(side_effect=[owner_member, None])
        self.member_repo.add_member = AsyncMock(return_value=new_member)
        result = await self.use_case.execute(project_id="proj-1", user_id="user-1", new_user_id="user-2", role="member")
        assert result.role == "member"

    @pytest.mark.asyncio
    async def test_add_member_not_found(self):
        self.project_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute(project_id="proj-999", user_id="user-1", new_user_id="user-2")

    @pytest.mark.asyncio
    async def test_add_member_already_exists(self):
        project = ProjectModel(id="proj-1", owner_id="user-1", name="Test")
        owner_member = ProjectMemberModel(id="mem-1", project_id="proj-1", user_id="user-1", role="owner", joined_at=datetime.now(UTC))
        existing_member = ProjectMemberModel(id="mem-2", project_id="proj-1", user_id="user-2", role="member", joined_at=datetime.now(UTC))
        self.project_repo.get_by_id = AsyncMock(return_value=project)
        self.member_repo.get_by_project_and_user = AsyncMock(side_effect=[owner_member, existing_member])
        with pytest.raises(ConflictException):
            await self.use_case.execute(project_id="proj-1", user_id="user-1", new_user_id="user-2")


class TestRemoveMemberUseCase:
    def setup_method(self):
        self.project_repo = MagicMock(spec=ProjectRepositoryInterface)
        self.member_repo = MagicMock(spec=ProjectMemberRepositoryInterface)
        self.use_case = RemoveMemberUseCase(self.project_repo, self.member_repo)

    @pytest.mark.asyncio
    async def test_remove_member_success(self):
        project = ProjectModel(id="proj-1", owner_id="user-1", name="Test")
        owner_member = ProjectMemberModel(id="mem-1", project_id="proj-1", user_id="user-1", role="owner", joined_at=datetime.now(UTC))
        target_member = ProjectMemberModel(id="mem-2", project_id="proj-1", user_id="user-2", role="member", joined_at=datetime.now(UTC))
        self.project_repo.get_by_id = AsyncMock(return_value=project)
        self.member_repo.get_by_project_and_user = AsyncMock(side_effect=[owner_member, target_member])
        self.member_repo.remove_member = AsyncMock(return_value=True)
        result = await self.use_case.execute(project_id="proj-1", user_id="user-1", target_user_id="user-2")
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_remove_member_not_found(self):
        self.project_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute(project_id="proj-999", user_id="user-1", target_user_id="user-2")


class TestUpdateMemberRoleUseCase:
    def setup_method(self):
        self.project_repo = MagicMock(spec=ProjectRepositoryInterface)
        self.member_repo = MagicMock(spec=ProjectMemberRepositoryInterface)
        self.use_case = UpdateMemberRoleUseCase(self.project_repo, self.member_repo)

    @pytest.mark.asyncio
    async def test_update_member_role_success(self):
        project = ProjectModel(id="proj-1", owner_id="user-1", name="Test")
        owner_member = ProjectMemberModel(id="mem-1", project_id="proj-1", user_id="user-1", role="owner", joined_at=datetime.now(UTC))
        target_member = ProjectMemberModel(id="mem-2", project_id="proj-1", user_id="user-2", role="member", joined_at=datetime.now(UTC))
        updated_member = ProjectMemberModel(id="mem-2", project_id="proj-1", user_id="user-2", role="admin", joined_at=datetime.now(UTC))
        self.project_repo.get_by_id = AsyncMock(return_value=project)
        self.member_repo.get_by_project_and_user = AsyncMock(side_effect=[owner_member, target_member])
        self.member_repo.update_member_role = AsyncMock(return_value=updated_member)
        result = await self.use_case.execute(project_id="proj-1", user_id="user-1", target_user_id="user-2", new_role="admin")
        assert result.role == "admin"

    @pytest.mark.asyncio
    async def test_update_member_role_not_found(self):
        self.project_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute(project_id="proj-999", user_id="user-1", target_user_id="user-2", new_role="admin")
