from __future__ import annotations

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import BigInteger, String, ForeignKey, Integer, Numeric, Enum, Text
from sqlalchemy.dialects.postgresql import BYTEA

from datetime import datetime, date
from typing import Literal

from .base import Base, BaseSub


Language = Literal['ru', 'uz', 'en']


class Fermer(Base):
    __tablename__ = 'fermers'
    
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    telegram_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    phone: Mapped[str | None] = mapped_column(String(100))
    address: Mapped[str | None] = mapped_column(String(500))
    location: Mapped[str | None] = mapped_column(String(200))
    login: Mapped[str | None] = mapped_column(String(100))
    username: Mapped[str | None] = mapped_column(String(50))
    avatar: Mapped[bytes | None] = mapped_column(BYTEA)
    isactive: Mapped[bool | None]
    inserted_time: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_time: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    other_contact: Mapped[str | None] = mapped_column(String)
    rayting: Mapped[int | None]
    region_id: Mapped[int | None]
    language: Mapped[Language] = mapped_column(Enum('ru', 'uz', 'en', name='lang_enum'))
    
    offers: Mapped[list['Offer']] = relationship(back_populates='fermer')


class Offer(Base):
    __tablename__ = 'seller_offers'
    
    fermer_id: Mapped[int] = mapped_column(Integer, ForeignKey('fermers.id'))
    is_active: Mapped[bool | None]
    inserted_by: Mapped[str | None] = mapped_column(String(50), default='TelegramBot')
    updated_by: Mapped[str | None] = mapped_column(String(50), default='TelegramBot')
    inserted_time: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_time: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )
    offer_num: Mapped[str | None] = mapped_column(String(20))
    head_description: Mapped[str | None] = mapped_column(String(50))
    foto_video_file_name: Mapped[str | None] = mapped_column(String(400))
    seller_price: Mapped[Numeric | None] = mapped_column(Numeric(18, 6))
    seller_quantity: Mapped[Numeric | None] = mapped_column(Numeric(18, 6))
    seller_sum: Mapped[Numeric | None] = mapped_column(Numeric(18, 6))
    pack_quantity: Mapped[Numeric | None] = mapped_column(Numeric(18, 6))
    minimal_quantity: Mapped[Numeric | None] = mapped_column(Numeric(18, 6))
    currency_types_id: Mapped[int | None]
    pack_descript: Mapped[str | None] = mapped_column(String(400))
    offer_status_id: Mapped[int| None]
    offer_start_date: Mapped[date | None]
    offer_end_date: Mapped[date| None]
    location: Mapped[str | None] = mapped_column(String(200))
    region_id: Mapped[int | None]
    goods_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('goods.id'))
    description: Mapped[str | None] = mapped_column(String(5000))
    PictureId: Mapped[int | None] = mapped_column(Integer, ForeignKey('Pictures.Id'))
    FilePath: Mapped[str | None] = mapped_column(Text)
    
    fermer: Mapped[Fermer] = relationship(back_populates='offers')
    good: Mapped['Good'] = relationship(back_populates='offers')
    picture: Mapped['Picture'] = relationship(back_populates='offer')
    

class Good(Base):
    __tablename__ = 'goods'
    
    goods_name: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    inserted_by: Mapped[str | None] = mapped_column(String(50), default='TelegramBot')
    updated_by: Mapped[str | None] = mapped_column(String(50), default='TelegramBot')
    inserted_time: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_time: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )
    islicensable: Mapped[bool | None]
    isclientrestricted: Mapped[bool | None]
    unit_types_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('unit_types.id'))
    goods_categories_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('goods_categories.id'))
    tnved_code: Mapped[str | None] = mapped_column(String(15))
    is_hi_liquid: Mapped[bool | None]
    tnved_id: Mapped[int | None]
    goods_name_ru: Mapped[str | None] = mapped_column(String(50))
    goods_name_uz: Mapped[str | None] = mapped_column(String(50))
    goods_name_en: Mapped[str | None] = mapped_column(String(50))
    
    unit_types: Mapped['UnitTypes'] = relationship(back_populates='goods')
    offers: Mapped[list[Offer]] = relationship(back_populates='good')
    good_category: Mapped['Good_Category'] = relationship(back_populates='goods')


class UnitTypes(Base):
    __tablename__ = 'unit_types'
    
    unit_types_name: Mapped[str | None] = mapped_column(String(50))
    unit_types_name_ru: Mapped[str] = mapped_column(String(50), nullable=False)
    unit_types_name_uz: Mapped[str] = mapped_column(String(50), nullable=False)
    unit_types_name_en: Mapped[str] = mapped_column(String(50), nullable=False)
    unit_code: Mapped[str | None] = mapped_column(String(10))
    inserted_by: Mapped[str | None] = mapped_column(String(50), default='TelegramBot')
    updated_by: Mapped[str | None] = mapped_column(String(50), default='TelegramBot')
    inserted_time: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_time: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    goods: Mapped[Good] = relationship(back_populates='unit_types')


class Good_Category(Base):
    __tablename__ = 'goods_categories'
    
    goods_categories_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    goods_categories_name_ru: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    goods_categories_name_uz: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    goods_categories_name_en: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    goods_code: Mapped[str | None] = mapped_column(String(10))
    is_restricted: Mapped[bool | None]
    inserted_by: Mapped[str | None] = mapped_column(String(50), default='TelegramBot')
    updated_by: Mapped[str | None] = mapped_column(String(50), default='TelegramBot')
    inserted_time: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_time: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_active: Mapped[bool | None]
    
    goods: Mapped[list[Good]] = relationship(back_populates='good_category')
    

class Picture(BaseSub):
    __tablename__ = 'Pictures'
    
    Id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    FilePath: Mapped[str | None] = mapped_column(Text())
    Image: Mapped[bytes | None] = mapped_column(BYTEA)
    
    offer: Mapped[Offer] = relationship(back_populates='picture')
    