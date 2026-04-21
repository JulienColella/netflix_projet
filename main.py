from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from db import get_connection

app = FastAPI()


class Film(BaseModel):
    id: int | None = None
    nom: str
    note: float | None = None
    dateSortie: int
    image: str | None = None
    video: str | None = None
    genreId: int | None = None

class User(BaseModel):
    pseudo: str
    email: str
    password: str

class Visionnage(BaseModel):
    user_id: int
    film_id: int



@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/films")
async def get_films(page: int = 1, per_page: int = 10, genre: int | None = None):
    with get_connection() as conn:
        cursor = conn.cursor()
        offset = (page - 1) * per_page
        if genre is not None:
            cursor.execute(f"SELECT * FROM Film WHERE Genre_ID={genre} ORDER BY DateSortie DESC LIMIT {per_page} OFFSET {offset}")
        else:
            cursor.execute(f"SELECT * FROM Film ORDER BY DateSortie DESC LIMIT {per_page} OFFSET {offset}")
        res = cursor.fetchall()
        return [dict(row) for row in res]



@app.post("/utilisateurs")
async def register(user: User):
    """Créer un compte utilisateur."""
    with get_connection() as conn:
        cursor = conn.cursor()
        # Utilisation des f-strings comme demandé
        cursor.execute(f"""
            INSERT INTO Utilisateur (AdresseMail, Pseudo, MotDePasse)  
            VALUES('{user.email}', '{user.pseudo}', '{user.password}')
        """)
        conn.commit()
        return {"message": "Utilisateur créé"}

@app.post("/visionnages")
async def record_view(v: Visionnage):
    """Enregistrer un film vu par un utilisateur."""
    with get_connection() as conn:
        cursor = conn.cursor()
        # On utilise la table Genre_Utilisateur pour lier User et Film
        cursor.execute(f"""
            INSERT INTO Genre_Utilisateur (ID_Genre, ID_User) 
            VALUES ({v.film_id}, {v.user_id})
        """)
        conn.commit()
        return {"message": "Visionnage enregistré"}

@app.get("/utilisateurs/{id}/historique")
async def get_history(id: int):
    """Voir les films vus par un utilisateur spécifique."""
    with get_connection() as conn:
        cursor = conn.cursor()
        # La jointure permet de récupérer les détails du film via la table de liaison
        cursor.execute(f"""
            SELECT Film.* FROM Film 
            JOIN Genre_Utilisateur ON Film.ID = Genre_Utilisateur.ID_Genre 
            WHERE Genre_Utilisateur.ID_User = {id}
        """)
        res = cursor.fetchall()
        return [dict(row) for row in res]
    
@app.get("/genres/{id}/films")
async def get_films_by_genre(id: int):
    """Films appartenant à un genre précis."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM Film WHERE Genre_ID = {id}")
        res = cursor.fetchall()
        return [dict(row) for row in res]

@app.get("/films/populaires")
async def get_popular():
    """Statistiques : les films les plus visionnés."""
    with get_connection() as conn:
        cursor = conn.cursor()
        # On groupe par film et on compte les utilisateurs
        cursor.execute("""
            SELECT Film.Nom, COUNT(Genre_Utilisateur.ID_User) as vues
            FROM Film
            JOIN Genre_Utilisateur ON Film.ID = Genre_Utilisateur.ID_Genre
            GROUP BY Film.ID
            ORDER BY vues DESC
            LIMIT 5
        """)
        res = cursor.fetchall()
        return [dict(row) for row in res]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)