import token

from fastapi import FastAPI, HTTPException, Header
import jwt
from pydantic import BaseModel
from db import get_connection
import jwt

SECRET_KEY = "secret"
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

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class Preference(BaseModel):
    genre_id: int


@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/films")
async def get_films(page: int = 1, per_page: int = 20, genre_ID: int | None = None):
    with get_connection() as conn:
        cursor = conn.cursor()
        offset = (page - 1) * per_page
        
        # Filtre Genre
        where_clause = f"WHERE Genre_ID = {genre_ID}" if genre_ID is not None else ""
        
        
        cursor.execute(f"SELECT COUNT(*) as total FROM Film {where_clause}")
        total = cursor.fetchone()["total"]
        
        
        cursor.execute(f"""
            SELECT * FROM Film {where_clause} 
            ORDER BY DateSortie DESC LIMIT {per_page} OFFSET {offset}
        """)
        

        res = cursor.fetchall()
        
        return {
            "data": [dict(row) for row in res],
            "page": page,
            "per_page": per_page,
            "total": total
        }



@app.post("/auth/register")
async def register(user: User):
    """Créer un compte utilisateur."""
    with get_connection() as conn:
        cursor = conn.cursor()
        #erreurs de validation : email, pseudo ou mot de passe manquant
        if not user.email or not user.password or not user.pseudo:
            raise HTTPException(status_code=422, detail="Email, pseudo et mot de passe sont requis")
        #si l'adresse mail existe déjà, on refuse l'inscription
        cursor.execute(f"SELECT * FROM Utilisateur WHERE AdresseMail='{user.email}'")
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="Email déjà utilisé")
        #si le pseudo existe déjà, on refuse l'inscription
        cursor.execute(f"SELECT * FROM Utilisateur WHERE Pseudo='{user.pseudo}'")  
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="Pseudo déjà utilisé")


#ajout d'un nouvel utilisateur dans la base de données
        cursor.execute(f"""
            INSERT INTO Utilisateur (AdresseMail, Pseudo, MotDePasse)  
            VALUES('{user.email}', '{user.pseudo}', '{user.password}')
        """)
        conn.commit()
        token = jwt.encode({"sub": user.email}, SECRET_KEY, algorithm="HS256")
        return TokenResponse(access_token=token, token_type="bearer")
        
        

@app.post("/auth/login")
async def login(user: User):
    """Authentifier un utilisateur."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if not user.email or not user.password:
            raise HTTPException(status_code=422, detail="Email et mot de passe sont requis")
        cursor.execute(f"""
            SELECT * FROM Utilisateur 
            WHERE AdresseMail='{user.email}' AND MotDePasse='{user.password}'
        """)
        res = cursor.fetchone()
        #si email ou mdp vide on refuse la connexion
        
        if res:
            token = jwt.encode({"sub": user.email}, SECRET_KEY,algorithm="HS256")
            return TokenResponse(access_token=token, token_type="bearer")
            
        else:
            raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")


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

@app.get("/user/{id}/historique")
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


@app.get("/genres")
async def get_genres():
    """Liste de tous les genres disponibles."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Genre order by Type ASC")
        res = cursor.fetchall()
        return [dict(row) for row in res]

@app.get("/films/{films_id}")
async def get_film(films_id: int):
    """Détails d'un film spécifique."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM Film WHERE ID = {films_id}")
        res = cursor.fetchone()
        if res:
            return dict(res)
        else:
            raise HTTPException(status_code=404, detail="Film non trouvé")
        








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


@app.post("/preferences", status_code=201)
async def add_preference(preference : Preference, authorization: str = Header(...)):
    """Ajouter un genre préféré pour un utilisateur."""
    token = authorization.split(" ")[1]  # Extraire le token du header
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_email = payload.get("sub")
        if not user_email:
            raise HTTPException(status_code=401, detail="Token invalide")
        
        with get_connection() as conn:
            cursor = conn.cursor()
            # Récupérer l'ID de l'utilisateur à partir de son email
            cursor.execute(f"SELECT ID FROM Utilisateur WHERE AdresseMail='{user_email}'")
            user = cursor.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
            
            user_id = user["ID"]
            # Ajouter la préférence dans la table Genre_Utilisateur
            cursor.execute(f"""
                INSERT INTO Genre_Utilisateur (ID_Genre, ID_User) 
                VALUES ({preference.genre_id}, {user_id})
            """)
            conn.commit()
            return {"message": "Préférence ajoutée"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")


















if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)