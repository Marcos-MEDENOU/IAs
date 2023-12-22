import os
import sqlite3
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.exc import OperationalError
import mysql.connector
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text
import requests
from bs4 import BeautifulSoup
import random
from models import storage

# Créer la fenêtre principale
window = tk.Tk()
window.title("HighFive Scrapper")
window.geometry("340x400")

# Obtenir la taille de l'écran et centrer la fenêtre
largeur_ecran = window.winfo_screenwidth()
hauteur_ecran = window.winfo_screenheight()
x = (largeur_ecran - window.winfo_reqwidth()) // 2
y = (hauteur_ecran - window.winfo_reqheight()) // 2
window.geometry("+{}+{}".format(x, y))

# Charger l'icône personnalisée
icone = Image.open("logo-2.8eecb413.ico")
largeur_voulue = 64
hauteur_voulue = 64
icone = icone.resize((largeur_voulue, hauteur_voulue), Image.LANCZOS)
icone = ImageTk.PhotoImage(icone)
window.iconphoto(False, icone)

# Créer un frame pour le contenu
content_frame = ttk.Frame(window, padding=0, width=400)
content_frame.grid(row=0, column=0, padx=5, pady=2)

# Entrée pour la thématique
thema_label = ttk.Label(content_frame, text="Saisir une thématique:", font=("Arial", 10))
thema_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

thema_entry = ttk.Entry(content_frame, font=("Arial", 10))
thema_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

# Connexion à la base de données
db_label = ttk.Label(content_frame, text="CONNEXION BASE DE DONNEE", font=("Arial", 14), foreground='red')
db_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="w")

content_frame.columnconfigure(0, weight=2)
content_frame.rowconfigure(3, weight=2)

# Paramètres de la base de données
db_params = [
    # ("DB_CONNECTION", ""),
    ("DB_HOST", ""),

    ("DB_DATABASE", ""),
    ("DB_USERNAME", ""),
    ("DB_PASSWORD", ""),
    ("DB_PORT", ""),
]
db_entries = []
row_num = 2
for param, placeholder in db_params:
    param_label = ttk.Label(content_frame, text=param, font=("Arial", 10))
    param_label.grid(row=row_num, column=0, padx=10, pady=10, sticky="w")
    param_entry = ttk.Entry(content_frame, font=("Arial", 10))
    param_entry.grid(row=row_num, column=1, padx=10, pady=10, sticky="w")
    param_entry.insert(0, placeholder)
    db_entries.append(param_entry)
    row_num += 1

# Bouton de soumission
submit_button = ttk.Button(content_frame, text="Soumettre", command=lambda: submit_data())
submit_button.grid(row=row_num + 2, columnspan=2, pady=10)
# Créez un label vide pour afficher le statut de la connexion
connexion_status = tk.Label(content_frame, text="", font=("Arial", 10))
connexion_status.grid(row=row_num + 1, columnspan=2, pady=10)


def if_database_exists(host, user, password, database_name):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_name
        )
        cursor = connection.cursor()
        cursor.close()
        connection.close()
        return True
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            return False
        else:
            raise


def create_database_if_not_exist(host, user, password, database_name):
    if not if_database_exists(host, user, password, database_name):
        try:
            connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password
            )
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE {}".format(database_name))
            cursor.close()
            connection.close()
            print("La base de données '{}' a été créée avec succès.".format(database_name))
        except mysql.connector.Error as err:
            print("Erreur lors de la création de la base de données : ", err)
    else:
        print("La base de données '{}' existe déjà.".format(database_name))


def create_database_table(DATABASE_URL, primary_key=None):
    # Définir les colonnes de la table (nom et type de colonne)
    columns = [
        ('id', Integer, primary_key == True),
        ('instruction', Text),
        ('detail', Text),
        ('output', Text),
    ]

    # Créer une connexion à la base de données
    engine = create_engine(DATABASE_URL)

    # Créer un objet MetaData
    metadata = MetaData()

    # Nom de la table que vous voulez créer
    table_name = 'ia_training'

    # Définir la table avec les colonnes
    my_table = Table(
        table_name,
        metadata,
        *[Column(col_name, col_type) for col_name, col_type, *args in columns]
    )

    # Créer la table dans la base de données
    with engine.connect() as connection:
        my_table.create(connection)


# Fonction pour récupérer des URLs à partir de Google
def get_google_search_results(query):
    # Effectuer une recherche sur Google pour le mot-clé
    recherche_url = f'https://fr.wikipedia.org/wiki/{query}'

    # En-tête de l'agent utilisateur (User-Agent) pour simuler un navigateur
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/94.0.4606.71 Safari/537.36'
    }

    # Effectuer une requête HTTP GET pour récupérer le contenu de la page de recherche Google
    response = requests.get(recherche_url, headers=headers)

    # Vérifier si la requête a réussi
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Supprimer la balise <header> et son contenu
        header = soup.find('script')
        footer =soup.find('footer')
        head =soup.find('head')

        if header:
            header.decompose()

        if footer:
            footer.decompose()

        if head:
            head.decompose()

        # Extraire le contenu restant
        page_content = soup

        print(page_content)
    else:
        return None

def submit_data():
    data = []
    print("Données saisies :")
    thematique = thema_entry.get()
    print("Thématique :", thematique)
    data.append(("DB_HOST", db_entries[0].get()))  # Remplacez l'index par l'ordre des champs
    data.append(("DB_DATABASE", db_entries[1].get()))
    data.append(("DB_USERNAME", db_entries[2].get()))
    data.append(("DB_PASSWORD", db_entries[3].get()))
    data.append(("DB_PASSWORD", db_entries[4].get()))
    print(data)
    # for param, entry in zip([param for param, _ in db_params], db_entries):
    # print(param, ":", entry.get())
    # pass

    try:
        if os.getenv('DATABASE_MODE') == 'test':
            engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
        else:
            engine = create_engine(
                # 'mysql+mysqldb://{}:{}@{}/{}'.format(
                # os.getenv('DATABASE_USERNAME'),
                # os.getenv('DATABASE_PASSWORD'),
                # os.getenv('DATABASE_HOSTNAME'),
                #  os.getenv('DATABASE_NAME'),
                # )
                'mysql+mysqldb://{}:{}@{}:{}/{}'.format(
                    data[2][1],
                    data[3][1],
                    data[1][1],
                    data[4][1],
                    data[0][1]
                )
            )

        print(data[2][1]),
        print(data[3][1]),
        print(data[1][1]),
        print(data[0][1]),
        metadata = MetaData()
        my_table = Table('my_tabl3', metadata, Column('id', Integer, primary_key=True), Column('name', String(255)))
        metadata.create_all(engine)

        print("Table 'my_table' créée avec succès dans la base de données.")
    except OperationalError as e:
        # Sinon bah, affiche donc un message d'erreur
        print("Erreur de connexion à la base de données : Impossible de se connecter.")
        connexion_status.config(text="Connexion échoué", fg="red")
        # Est-ce la base de donnée qui n'existe pas ? Si oui crée la
        if if_database_exists(
                # os.getenv('DATABASE_HOSTNAME'),
                # os.getenv('DATABASE_USERNAME'),
                # os.getenv('DATABASE_PASSWORD'),
                # os.getenv('DATABASE_NAME'),*
                data[0][1],
                data[2][1],
                data[3][1],
                data[1][1]
        ):
            print("La base de données existe.")

            connexion_status.config(text="Connexion réussie", fg="green")
            get_google_search_results(thematique)
        else:
            print("La base de données n'existe pas.")
            create_database_if_not_exist(
                data[0][1],
                data[2][1],
                data[3][1],
                data[1][1]
            )
            connexion_status.config(text="Connexion réussie", fg="green")

            DATABASE_URL = 'mysql+mysqldb://{}:{}@{}:{}/{}'.format(
                data[2][1],
                data[3][1],
                data[0][1],
                data[4][1],
                data[1][1]
            )
            create_database_table(DATABASE_URL)
            get_google_search_results(thematique)



        # Lancer la boucle principale


window.mainloop()
