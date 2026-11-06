from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.postgresql import get_postgresql_db
from fastapi import Depends
from sqlalchemy import insert, select, update, delete, func, exists, desc, asc, or_
from sqlalchemy.orm import joinedload

from app.models.post_model import Post
from app.models.member_model import Member
from app.schemas.post_schema import PostCreateDTO
from app.enums.post_enum import PostSortEnum, PostSearchEnum


# repository에서 하면 안되는 것들:
# 1. 예외 처리(db에 접근하는 순수한 함수들로만 이루어져야 하므로)
class PostRepository:
    # db가 필요
    # 생성자 주입(레포지토리가 호출되는 동시에 db 정보도 호출되어야 하므로 class가 호출될 때 자동으로 실행되는 생성자(init)에 db를 넣음)
    def __init__(self, db:AsyncSession):
        self.db = db

    # 순수함수
    # 게시글 작성(이름을 save, create로 하는 게 약속)
    async def create_post(self, member_id: int, post: PostCreateDTO):
        post.model_dump()

        query = (
            insert(Post)
            .values(
                **post.model_dump(),
                member_id=member_id
            )
            .returning(
                Post.id
            )
        )

        result = await self.db.execute(query)
        await self.db.commit()
        new_post_id = result.scalar_one()
        return new_post_id


    # 게시글 1개 조회
    async def find_post_by_id(self, post_id: int):
        query = (
            select(Post)
                .options(joinedload(Post.member))
                .where(Post.id == post_id)
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    # 게시글 전체 조회(페이지네이션 + 정렬)
    # 최신순("latest"), 오래된 순("oldest"), 조회순("views")
    async def find_post_by_paging(
            self,
            offset: int,
            limit: int,
            sort_by: PostSortEnum = PostSortEnum.LATEST.value
    ):
        query = (
            select(Post).options(joinedload(Post.member))
        )

        if sort_by == PostSortEnum.OLDEST:
            query = query.order_by(asc(Post.id))
        elif sort_by == PostSortEnum.VIEWS:
            query = query.order_by(desc(Post.post_read_count), desc(Post.id))
        elif sort_by == PostSortEnum.LATEST:
            query = query.order_by(desc(Post.id))

        # 정렬된 상태에서 offset, limit
        query = query.offset(offset).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    # 게시글 전체 개수 조회
    async def count_posts(self) -> int:
        query = (
            select(func.count())
                .select_from(Post)
        )

        result = await self.db.execute(query)
        return result.scalar_one()
    

    # 게시글 검색(제목, 내용, 작성자, 제목+내용)
  # 게시글 검색(제목, 내용, 작성자, 제목+내용)
    async def search_posts(
        self,
        offset: int,
        limit: int,
        sort_by: PostSortEnum = PostSortEnum.LATEST.value,
        search_keyword:PostSearchEnum = PostSearchEnum.TITLE.value, # 구분점 
        keyword: str | None = None # 사용자 검색어 "ABC"
    ):

        # 검색 + 페이지네이션 베이스 쿼리
        query = (
            select(Post).options(joinedload(Post.member))
        )

        # 검색 + 페이지네이션 게시글의 개수 쿼리
        count_query = (
            select(func.count()).select_from(Post)
        )

        if keyword and search_keyword:
            search_word = f"%{keyword}%"
            condition = None

            if search_keyword == PostSearchEnum.TITLE:
                condition = Post.post_title.like(search_word)

            elif search_keyword == PostSearchEnum.CONTENT:
                condition = Post.post_content.like(search_word)

            elif search_keyword == PostSearchEnum.WRITER:
                query = query.join(Post.member)
                count_query = count_query.join(Post.member)
                condition = Member.member_name.like()

            elif search_keyword == PostSearchEnum.TITLE_CONTENT:
                condition = or_(
                    Post.post_title.like(search_word),
                    Post.post_content.like(search_word)
                )

            if condition is not None:
                query = query.where(condition)
                count_query = count_query.where(condition)


        if sort_by == PostSortEnum.OLDEST:
            query = query.order_by(asc(Post.id))
        elif sort_by == PostSortEnum.VIEWS:
            query = query.order_by(desc(Post.post_read_count), desc(Post.id))
        elif sort_by == PostSortEnum.LATEST:
            query = query.order_by(desc(Post.id))

        # 정렬된 상태에서 offset, limit
        query = query.offset(offset).limit(limit)
        result = await self.db.execute(query)

        posts = list(result.scalars().all())
        count_result = await self.db.execute(count_query)
        total_count = count_result.scalar_one()

        return posts, total_count


    # 게시글 수정
    async def update_post(self, post_id: int, update_data: dict) -> int:
        if not update_data:
            return None

        query = (
            update(Post)
            .values(**update_data, post_updated_at=func.now())
            .where(Post.id == post_id)
            .returning(Post.id)
        )

        result = await self.db.execute(query)
        await self.db.commit()

        updated_post_id = result.scalar_one_or_none()
        return updated_post_id


    # 게시글 삭제
    async def delete_post(self, post_id: int) -> bool:
        query = (
            delete(Post)
            .where(Post.id == post_id)
        )

        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0



# 주입 팩토리 메서드
def get_post_repository(db: AsyncSession = Depends(get_postgresql_db)):
    return PostRepository(db)

