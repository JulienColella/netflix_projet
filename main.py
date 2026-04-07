from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from db import get_connection

app = FastAPI()


@app.get("/ping")
def ping():
    return {"message": "pong"}

class Film(BaseModel):
    id: int | None = None
    nom: str
    note: float | None = None
    dateSortie: int
    image: str | None = None
    video: str | None = None
    genreId: int | None = None

class user(BaseModel):
    id: int | None = None
    pseudo: str
    email: str
    password: str

@app.post("/user")
async def register(user : user):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            INSERT INTO "User" (Pseudo,Email,Password)  
            VALUES('{user.pseudo}','{user.email}','{user.password}') RETURNING *
            """)
        res = cursor.fetchone()
        print(res)
        return [dict(row) for row in res]


@app.post("/film")
async def createFilm(film : Film):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            INSERT INTO Film (Nom,Note,DateSortie,Image,Video)  
            VALUES('{film.nom}',{film.note},{film.dateSortie},'{film.image}','{film.video}') RETURNING *
            """)
        res = cursor.fetchone()
        print(res)
        return [dict(row) for row in res]

@app.get("/films")
async def getFilms( page: int = 1, per_page: int = 10, genre : int | None = None):
    with get_connection() as conn:
        cursor = conn.cursor()
        if genre is not None:
            cursor.execute(f"SELECT * FROM Film WHERE Genre_Id={genre} ORDER BY dateSortie DESC LIMIT {per_page} OFFSET {(page - 1) * per_page} ")
        else:
            cursor.execute(f"SELECT * FROM Film ORDER BY dateSortie DESC LIMIT {per_page} OFFSET {(page - 1) * per_page} ")
        res = cursor.fetchall()
        print(res)
        return [dict(row) for row in res]

@app.get("/films/{id}")
async def getFilm(id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM Film WHERE Id={id}")
        res = cursor.fetchone()
        if res is None:
            raise HTTPException(status_code=404, detail="Film non trouvé")
        print(res)
        return [dict(row) for row in res]

@app.get("/genres")
async def getGenres():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Genre")
        res = cursor.fetchall()
        print(res)
        return [dict(row) for row in res]




if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
