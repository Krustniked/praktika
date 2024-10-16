from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Table, Column, ForeignKey


class Base(DeclarativeBase):
    pass

answers_tokens = Table(
    "answers_tokens",
    Base.metadata,
    Column("answer", ForeignKey("answer.id"), primary_key=True),
    Column("token", ForeignKey("token.id"), primary_key=True),
)
# https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#many-to-many


class Answer(Base):
  __tablename__ = "answer"
  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  text: Mapped[str] = mapped_column(String(2000))
  tokens: Mapped[list["Token"]] = relationship(secondary=answers_tokens, back_populates="answers")
  
  def to_dict(self):
     return {
        "id":self.id,
        "text":self.text,
        "tokens":[token.text for token in self.tokens] if self.tokens else []
     }

class Token(Base):
   __tablename__ = "token"
   id: Mapped[int] = mapped_column(Integer, primary_key=True)
   text: Mapped[str] = mapped_column(String(300))
   answers: Mapped[list["Answer"]] = relationship(secondary=answers_tokens, back_populates="tokens")
   
   def to_dict(self):
      return {
         "id":self.id,
         "token":self.text,
         "answers":[answer.id for answer in self.answers] if self.answers else []
      }

