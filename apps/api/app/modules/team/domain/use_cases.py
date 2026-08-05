from datetime import UTC, datetime

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.modules.team.domain.interfaces import (
    TeamMemberRepositoryInterface,
    TeamRepositoryInterface,
)
from app.modules.team.domain.models import TeamMemberModel, TeamModel


class CreateTeamUseCase:
    def __init__(
        self,
        team_repo: TeamRepositoryInterface,
        member_repo: TeamMemberRepositoryInterface,
    ):
        self.team_repo = team_repo
        self.member_repo = member_repo

    async def execute(
        self,
        name: str,
        owner_id: str,
        description: str | None = None,
    ) -> TeamModel:
        self._validate_name(name)

        team = TeamModel(
            name=name.strip(),
            description=description.strip() if description else None,
            owner_id=owner_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        created = await self.team_repo.create(team)

        owner_member = TeamMemberModel(
            team_id=created.id,
            user_id=owner_id,
            role="owner",
            joined_at=datetime.now(UTC),
        )
        await self.member_repo.add_member(owner_member)

        return created

    def _validate_name(self, name: str) -> None:
        if not name or not name.strip():
            raise ValidationException("Team name is required")
        if len(name.strip()) < 3:
            raise ValidationException("Team name must be at least 3 characters")
        if len(name.strip()) > 255:
            raise ValidationException("Team name must be less than 255 characters")


class ListTeamsUseCase:
    def __init__(
        self,
        team_repo: TeamRepositoryInterface,
        member_repo: TeamMemberRepositoryInterface,
    ):
        self.team_repo = team_repo
        self.member_repo = member_repo

    async def execute(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> dict:
        teams = await self.team_repo.list_by_user(
            user_id=user_id, skip=skip, limit=limit
        )

        result = []
        for team in teams:
            members = await self.member_repo.list_members(str(team.id))
            result.append(
                {
                    "id": str(team.id),
                    "name": team.name,
                    "description": team.description,
                    "owner_id": str(team.owner_id),
                    "member_count": len(members),
                    "created_at": team.created_at.isoformat(),
                    "updated_at": team.updated_at.isoformat(),
                }
            )

        return {
            "items": result,
            "total": len(result),
            "skip": skip,
            "limit": limit,
        }


class GetTeamUseCase:
    def __init__(
        self,
        team_repo: TeamRepositoryInterface,
        member_repo: TeamMemberRepositoryInterface,
    ):
        self.team_repo = team_repo
        self.member_repo = member_repo

    async def execute(
        self, team_id: str, user_id: str
    ) -> dict:
        team = await self.team_repo.get_by_id(team_id)
        if not team:
            raise NotFoundException("Team", team_id)

        membership = await self.member_repo.get_by_team_and_user(
            team_id, user_id
        )
        if not membership:
            raise ValidationException("You are not a member of this team")

        members = await self.member_repo.list_members(team_id)
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
            "id": str(team.id),
            "name": team.name,
            "description": team.description,
            "owner_id": str(team.owner_id),
            "members": member_list,
            "member_count": len(member_list),
            "created_at": team.created_at.isoformat(),
            "updated_at": team.updated_at.isoformat(),
        }


class AddTeamMemberUseCase:
    def __init__(
        self,
        team_repo: TeamRepositoryInterface,
        member_repo: TeamMemberRepositoryInterface,
    ):
        self.team_repo = team_repo
        self.member_repo = member_repo

    async def execute(
        self, team_id: str, user_id: str, target_user_id: str, role: str = "member"
    ) -> TeamMemberModel:
        team = await self.team_repo.get_by_id(team_id)
        if not team:
            raise NotFoundException("Team", team_id)

        requester_membership = await self.member_repo.get_by_team_and_user(
            team_id, user_id
        )
        if not requester_membership or requester_membership.role not in (
            "owner",
            "admin",
        ):
            raise ValidationException("Only owners and admins can add members")

        existing = await self.member_repo.get_by_team_and_user(
            team_id, target_user_id
        )
        if existing:
            raise ConflictException("User is already a member of this team")

        if role not in ("admin", "member"):
            raise ValidationException("Invalid role")

        member = TeamMemberModel(
            team_id=team_id,
            user_id=target_user_id,
            role=role,
            joined_at=datetime.now(UTC),
        )
        return await self.member_repo.add_member(member)


class RemoveTeamMemberUseCase:
    def __init__(
        self,
        team_repo: TeamRepositoryInterface,
        member_repo: TeamMemberRepositoryInterface,
    ):
        self.team_repo = team_repo
        self.member_repo = member_repo

    async def execute(
        self, team_id: str, user_id: str, target_user_id: str
    ) -> dict:
        team = await self.team_repo.get_by_id(team_id)
        if not team:
            raise NotFoundException("Team", team_id)

        requester_membership = await self.member_repo.get_by_team_and_user(
            team_id, user_id
        )
        if not requester_membership or requester_membership.role not in (
            "owner",
            "admin",
        ):
            raise ValidationException("Only owners and admins can remove members")

        target_membership = await self.member_repo.get_by_team_and_user(
            team_id, target_user_id
        )
        if not target_membership:
            raise NotFoundException("Member", target_user_id)

        if target_membership.role == "owner":
            raise ValidationException("Cannot remove the team owner")

        await self.member_repo.remove_member(team_id, target_user_id)
        return {"message": "Member removed successfully"}


class DeleteTeamUseCase:
    def __init__(
        self,
        team_repo: TeamRepositoryInterface,
        member_repo: TeamMemberRepositoryInterface,
    ):
        self.team_repo = team_repo
        self.member_repo = member_repo

    async def execute(self, team_id: str, user_id: str) -> dict:
        team = await self.team_repo.get_by_id(team_id)
        if not team:
            raise NotFoundException("Team", team_id)

        membership = await self.member_repo.get_by_team_and_user(
            team_id, user_id
        )
        if not membership or membership.role != "owner":
            raise ValidationException("Only the owner can delete a team")

        await self.team_repo.delete(team_id)
        return {"message": "Team deleted successfully"}
