from fastapi import Depends, HTTPException
from app.repositories.post_repository import PostRepository, get_post_repository
from app.repositories.member_repository import MemberRepository, get_member_repository
from app.schemas.post_schema import PostCreateDTO, PostResponseDTO, PostListResponseDTO, PostUpdateDTO
from app.schemas.common_schema import PageResponseDTO
from app.enums.post_enum import PostSortEnum, PostSearchEnum

# 예외처리
# 트랜잭션 관리
class PostService:

    def __init__(self, post_repo: PostRepository, member_repo: MemberRepository):
        self.post_repo = post_repo
        self.member_repo = member_repo

    # 게시글 작성
    async def write_post(self, member_id: int, post: PostCreateDTO) -> int:
        exists_member = await self.member_repo.exists_member_by_id(member_id)
        if not exists_member:
            raise HTTPException(
                status_code=404,
                detail="존재하지 않는 회원입니다."
            )
        new_post_id = await self.post_repo.create_post(member_id, post)
        return new_post_id

    # 게시글 1개 조회
    async def get_post_by_id(self, post_id: int) -> PostResponseDTO:
        found_post = await self.post_repo.find_post_by_id(post_id)

        if not found_post:
            raise HTTPException(
                status_code=404,
                detail="글이 존재하지 않습니다"
            )

        return PostResponseDTO.model_validate(found_post)

    # 게시글 전체 조회(페이지, 정렬)
    async def search_posts_by_paging(
            self,
            offset: int = 1,
            limit: int = 10,
            sort_by: PostSortEnum = PostSortEnum.LATEST.value,
            search_keyword: PostSearchEnum = PostSearchEnum.TITLE.value,
            keword: str | None = None

    ) -> PageResponseDTO:
        posts = await self.post_repo.find_post_by_paging(offset, limit, sort_by, search_keyword, keword)
        total_count = await self.post_repo.count_posts()
        total_pages = (total_count + limit - 1) // limit if limit > 0 else 1
        items = [PostListResponseDTO.model_validate(post) for post in posts]

        return PageResponseDTO(
            total_count=total_count,
            total_page=total_pages,
            offset=offset,
            limit=limit,
            items=items
        )


    # 게시글 검색
    # 게시글 수정
    async def update_post(self, post_id: int, post: PostUpdateDTO):
        update_data = post.model_dump(exclude_unset=True)

        updated_post_id = await self.post_repo.update_post(post_id, update_data)

        return updated_post_id

    # 게시글 삭제
    async def remove_post(self, post_id) -> None:
        is_remove = await self.post_repo.delete_post(post_id)

        if not is_remove:
            raise HTTPException(
                status_code=404,
                detail="게시글이 존재하지 않습니다."
            )


# 레포지토리 주입 팩토리 함수
def get_post_service(
        post_repo: PostRepository = Depends(get_post_repository),
        member_repo: MemberRepository = Depends(get_member_repository)
    ):
    return PostService(post_repo, member_repo)