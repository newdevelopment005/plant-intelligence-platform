from app.core.exceptions import NotFoundException
from app.modules.auth.domain.interfaces import UserRepositoryInterface
from app.modules.auth.domain.models import UserModel


class GetUserProfileUseCase:
    def __init__(self, user_repo: UserRepositoryInterface):
        self.user_repo = user_repo

    async def execute(self, user_id: str) -> UserModel:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        return user


class UpdateUserProfileUseCase:
    def __init__(self, user_repo: UserRepositoryInterface):
        self.user_repo = user_repo

    async def execute(
        self,
        user_id: str,
        full_name: str | None = None,
        institution: str | None = None,
        department: str | None = None,
        bio: str | None = None,
        orcid_id: str | None = None,
    ) -> UserModel:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)

        if full_name is not None:
            user.full_name = full_name.strip()
        if institution is not None:
            user.institution = institution.strip() if institution else None
        if department is not None:
            user.department = department.strip() if department else None
        if bio is not None:
            user.bio = bio.strip() if bio else None
        if orcid_id is not None:
            user.orcid_id = orcid_id.strip() if orcid_id else None

        return await self.user_repo.update(user)
