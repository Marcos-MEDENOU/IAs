#!usr/bin/python3
"""
    Un Module de gestion de la base de donneer
    C"est le module permettant de gerer toutes les requetes sql que ce soit les operation d'insertion, update et autre jusqu'a la creation de nouvelle table
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, select
from sqlalchemy.orm import sessionmaker, scoped_session

load_dotenv()


class DBStorage:
    """
        Class representant le gestionnaire de base de donnees
    """
    # Models Classes


    """
        Handles storage for database
        engine : proprietes interne se connectant au type serveur de base de donner (mysql, sqlite, postgree)
        session : Elle permet de cree une session donner pour un utilisateur voulant mener des operation sur la base de donnee
    """
    __engine = None
    __session = None

    def __init__(self):
        """
        Initialize the database engine to work with
        Veuillez prendre exemple sur les requis des variables d'environnement afin de cree la base de donnee sur votre ordinateur
        """

        if os.getenv('DATABASE_MODE') == 'test':
            self.__engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
        else:
            self.__engine = create_engine(
                'mysql+mysqldb://{}:{}@{}/{}'.format(
                    os.getenv('DATABASE_USERNAME'),
                    os.getenv('DATABASE_PASSWORD'),
                    os.getenv('DATABASE_HOSTNAME'),
                    os.getenv('DATABASE_NAME'),
                )
            )

    def all(self, cls=None):
        """ 
        Methode all permet de recuperer toutes les donnes d'un model(table)
        NB : Pour traiter avec la base de donner on utilise l'ORM qui est sqlalchemy dont il faut avoir des notions
        """
        mod_dict = {}
        if cls:
            mod_class = self.__session.scalars(select(self.MC.get(cls))).all()
            for item in mod_class:
                key = str(item.__class__.__name__) + "." + str(item.id)
                mod_class[key] = item
        return mod_dict

    def new(self, obj):
        """ 
        Add a new object
        Ajouter un nouvel objet au model(table) cree
        """
        self.__session.add(obj)

    def get(self, cls, id):
        """
        Fetch a specific object
        Retirer un objet (donnee) du model (table) 
        """

        obj = self.__session.get(self.MC.get(cls), id)
        if obj:
            return obj
        return None

    def get_filter(self, cls, filter):
        result = self.__session.execute(select(self.MC.get(cls)).filter_by(**filter)).scalar_one()
        if result is not None:
            return result
        return None

    def count(self, cls):
        """
        Count all objects of a model
        Compter tous les objets (donnes) du model (table)
        """
        return len(self.all(cls))

    def save(self):
        """
        commits all changes of current database session
        """
        self.__session.commit()

    def delete(self, obj=None):
        """ deletes obj from current database session if not None """
        if obj is not None:
            self.__session.delete(obj)

    def reload(self):
        """
        Create all database table and a session
        Method permettant de creer les tables de la bases de donnee et d'attribuer une session a l'utilisation pour effectuer les operations
        Toutes les session sont gerer par l'ORM
        """
        # Base.metadata.drop_all(self.__engine)

        self.__session = scoped_session(
            sessionmaker(bind=self.__engine, expire_on_commit=False)
        )
