from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    TIMESTAMP,
    DECIMAL,
    Float
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.db import Base
 
# ========================
## ========================
# ========================
# ADMINS
# ========================
class Admin(Base):
    __tablename__ = "admins"

    admin_id = Column(Integer, primary_key=True)

    name = Column(String(100), nullable=False)

    email = Column(String(150), unique=True, nullable=False)

    password_hash = Column(Text, nullable=False)

    role = Column(String(50), default="admin")

    preferred_language = Column(
        String(10),
        default="en"
    )

    notification_enabled = Column(
        Boolean,
        default=True
    )

    latitude = Column(
        Float,
        nullable=True
    )

    longitude = Column(
        Float,
        nullable=True
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )

    # News created by admin
    created_news = relationship(
        "News",
        foreign_keys="News.author_id",
        back_populates="author"
    )

    # News approved by admin
    approved_news = relationship(
        "News",
        foreign_keys="News.approved_by",
        back_populates="approved_admin"
    )
# ========================
# # ========================
# USERS
# ========================
class User(Base):
    __tablename__ = "users"
 
    user_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True)
    mobile_number = Column(String(15), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    preferred_language = Column(String(10), default="en")
 
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
 
    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )
 
    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )
    notification_enabled = Column(
    Boolean,
    default=True
)
    # Relationships
    comments = relationship(
        "Comment",
        back_populates="user"
    )
 
    likes = relationship(
        "Like",
        back_populates="user"
    )
 
    bookmarks = relationship(
        "Bookmark",
        back_populates="user"
    )
 
    activities = relationship(
        "UserActivity",
        back_populates="user"
    )
 
    notifications = relationship(
        "Notification",
        back_populates="user"
    )
 
    poll_votes = relationship(
        "PollVote",
        back_populates="user"
    )
# ========================
# CATEGORIES
# ========================
class Category(Base):
    __tablename__ = "categories"
 
    category_id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
 
    # Relationships
    news = relationship("News", back_populates="category")
 
# ========================
# NEWS
# ========================
class News(Base):
    __tablename__ = "news"
 
    news_id = Column(Integer, primary_key=True)
 
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
 
    original_language = Column(
        String(10),
        default="en"
    )
 
    category_id = Column(
        Integer,
        ForeignKey("categories.category_id")
    )
 
    # Admin who created the news
    author_id = Column(
        Integer,
        ForeignKey("admins.admin_id")
    )
 
    news_type = Column(
        String(20),
        nullable=False,
        default="local"
    )
 
    country = Column(
    String(100),
    nullable=False,
    default="India"
)
    state = Column(String(100))
    district = Column(String(100))
    mandal = Column(String(100))
    city = Column(String(100))
    village = Column(String(100))
 
    status = Column(
        String(20),
        default="draft"
    )
    share_count = Column(
    Integer,
    default=0
)
    is_breaking = Column(
        Boolean,
        default=False
    )
 
    view_count = Column(
        Integer,
        default=0
    )
 
    like_count = Column(
        Integer,
        default=0
    )
 
    comment_count = Column(
        Integer,
        default=0
    )
 
    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )
 
    published_at = Column(
        TIMESTAMP
    )
 
    thumbnail_url = Column(Text)
 
    video_url = Column(
        String(1000),
        nullable=True
    )
 
    # Admin who approved the news
    approved_by = Column(
        Integer,
        ForeignKey("admins.admin_id")
    )
 
    approved_at = Column(
        TIMESTAMP
    )
 
    rejection_reason = Column(
        Text
    )
 
    # ========================
    # RELATIONSHIPS
    # ========================
 
    category = relationship(
        "Category",
        back_populates="news"
    )
 
    author = relationship(
        "Admin",
        foreign_keys=[author_id],
        back_populates="created_news"
    )
 
    comments = relationship(
        "Comment",
        back_populates="news",
        cascade="all, delete"
    )
 
    likes = relationship(
        "Like",
        back_populates="news",
        cascade="all, delete"
    )
 
    bookmarks = relationship(
        "Bookmark",
        back_populates="news",
        cascade="all, delete"
    )
 
    polls = relationship(
        "Poll",
        back_populates="news",
        cascade="all, delete"
    )
 
    activities = relationship(
        "UserActivity",
        back_populates="news"
    )
 
    translations = relationship(
        "NewsTranslation",
        back_populates="news"
    )
 
    audios = relationship(
        "NewsAudio",
        back_populates="news"
    )
 
    approved_admin = relationship(
        "Admin",
        foreign_keys=[approved_by],
        back_populates="approved_news"
    )
 
    media = relationship(
        "NewsMedia",
        back_populates="news",
        cascade="all, delete"
    )
# ========================
# NEWS MEDIA
# ========================
class NewsMedia(Base):
    __tablename__ = "news_media"
 
    media_id = Column(Integer, primary_key=True)
 
    news_id = Column(
        Integer,
        ForeignKey("news.news_id")
    )
 
    media_type = Column(String(20))
    media_url = Column(Text, nullable=False)
 
    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )
 
    news = relationship(
        "News",
        back_populates="media"
    )
# ========================
# LIKES
# ========================
class Like(Base):
    __tablename__ = "likes"
 
    like_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    news_id = Column(Integer, ForeignKey("news.news_id"))
    created_at = Column(TIMESTAMP, server_default=func.now())
 
    # Relationships
    user = relationship("User", back_populates="likes")
    news = relationship("News", back_populates="likes")
 
 
# ========================
# COMMENTS
# ========================
class Comment(Base):
    __tablename__ = "comments"
 
    comment_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    news_id = Column(Integer, ForeignKey("news.news_id"))
    parent_comment_id = Column(Integer, ForeignKey("comments.comment_id"))
 
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
 
    # Relationships
    user = relationship("User", back_populates="comments")
    news = relationship("News", back_populates="comments")
 
    replies = relationship("Comment")
 
 
# ========================
# BOOKMARKS
# ========================
class Bookmark(Base):
    __tablename__ = "bookmarks"
 
    bookmark_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    news_id = Column(Integer, ForeignKey("news.news_id"))
    created_at = Column(TIMESTAMP, server_default=func.now())
 
    # Relationships
    user = relationship("User", back_populates="bookmarks")
    news = relationship("News", back_populates="bookmarks")
 
 
# ========================
# POLLS
# ========================
class Poll(Base):
    __tablename__ = "polls"
 
    poll_id = Column(Integer, primary_key=True)
 
    news_id = Column(
        Integer,
        ForeignKey("news.news_id")
    )
 
    question = Column(
        Text,
        nullable=False
    )
 
    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )
 
    # Relationships
    news = relationship(
        "News",
        back_populates="polls"
    )
 
    options = relationship(
        "PollOption",
        back_populates="poll",
        cascade="all, delete"
    )
 
    votes = relationship(
        "PollVote",
        back_populates="poll",
        cascade="all, delete"
    )
 
 
# ========================
# POLL OPTIONS
# ========================
class PollOption(Base):
    __tablename__ = "poll_options"
 
    option_id = Column(
        Integer,
        primary_key=True
    )
 
    poll_id = Column(
        Integer,
        ForeignKey("polls.poll_id")
    )
 
    option_text = Column(
        String(255),
        nullable=False
    )
 
    votes_count = Column(
        Integer,
        default=0
    )
 
    # Relationships
    poll = relationship(
        "Poll",
        back_populates="options"
    )
 
    votes = relationship(
        "PollVote",
        back_populates="option",
        cascade="all, delete"
    )
 
# # ========================
# POLL VOTES
# ========================
class PollVote(Base):
    __tablename__ = "poll_votes"
 
    vote_id = Column(
        Integer,
        primary_key=True
    )
 
    poll_id = Column(
        Integer,
        ForeignKey("polls.poll_id")
    )
 
    option_id = Column(
        Integer,
        ForeignKey("poll_options.option_id")
    )
 
    user_id = Column(
        Integer,
        ForeignKey("users.user_id")
    )
 
    voted_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )
 
    poll = relationship(
        "Poll",
        back_populates="votes"
    )
 
    option = relationship(
        "PollOption",
        back_populates="votes"
    )
 
    user = relationship(
        "User",
        back_populates="poll_votes"
    )
# ========================
# USER ACTIVITY
# ========================
class UserActivity(Base):
    __tablename__ = "user_activity"
 
    activity_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    news_id = Column(Integer, ForeignKey("news.news_id"))
 
    action_type = Column(String(20))
    time_spent = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())
 
    # Relationships
    user = relationship("User", back_populates="activities")
    news = relationship("News", back_populates="activities")
 
 
# ========================
# NEWS TRANSLATIONS
# ========================
class NewsTranslation(Base):
    __tablename__ = "news_translations"
 
    translation_id = Column(
        Integer,
        primary_key=True
    )
 
    news_id = Column(
        Integer,
        ForeignKey("news.news_id")
    )
 
    language = Column(
        String(10),
        nullable=False
    )
 
    translated_title = Column(
        Text,
        nullable=False
    )
 
    translated_summary = Column(
        Text
    )
 
    translated_content = Column(
        Text,
        nullable=False
    )
 
    news = relationship(
        "News",
        back_populates="translations"
    )
 
 
# ========================
# NOTIFICATIONS
# ========================
class Notification(Base):
    __tablename__ = "notifications"
 
    notification_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    news_id = Column(Integer, ForeignKey("news.news_id"))
 
    title = Column(Text)
    message = Column(Text)
 
    type = Column(String(50))
    target_type = Column(String(20))
 
    is_read = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
 
    created_at = Column(TIMESTAMP, server_default=func.now())
    sent_at = Column(TIMESTAMP)
    expires_at = Column(TIMESTAMP)
 
    # Relationships
    user = relationship("User", back_populates="notifications")
    news = relationship("News")
 
 
# ========================
# NEWS AUDIO
# ========================
class NewsAudio(Base):
    __tablename__ = "news_audio"
 
    audio_id = Column(Integer, primary_key=True)
    news_id = Column(Integer, ForeignKey("news.news_id"))
    language = Column(String(10))
    audio_url = Column(Text)
    duration = Column(Integer)
    is_generated = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
 
    # Relationships
    news = relationship("News", back_populates="audios")
 
 