from typing import Union, Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

app = FastAPI()

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_name: str = Field(index=True)
    password: int | None = Field(default=None, index=True)
    email: str

# Use PostgreSQL URL
postgres_url = "postgresql://omniapi:omniapi@10.0.0.21/omniapi"
engine = create_engine(postgres_url, echo=True)  # echo=True logs SQL queries

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.put("/user/{id}", response_model=Hero)
def update_hero(id: int, updated_user: Hero, session: SessionDep):
    user = session.get(Hero, id)

    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    user.user_name = updated_user.user_name
    user.password = updated_user.password
    user.email = updated_user.email

    session.add(user)
    session.commit()
    session.refresh(user)

    return user
@app.post("/user")
def create_hero(hero: Hero, session: SessionDep) -> Hero:
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero

@app.get("/user")
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Hero]:
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes

@app.get("/user/{id}")
def read_hero(id: int, session: SessionDep) -> Hero:
    hero = session.get(Hero, id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero

@app.delete("/user/{id}")
def delete_hero(id: int, session: SessionDep):
    hero = session.get(Hero, id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"User Deleted": True}

@app.get("/api/word/unlimited/get")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
