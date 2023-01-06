from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Längst ner finns vår funktion för att skapa databasen.
# Denna funktion ska köras först om det inte redan finns en databas
# Denna funktion ska endast användas EN gång
# sedan bör man kommentera/ta bort ropet(call) på funktionen
Base = declarative_base()
engine = create_engine('sqlite:///Idrottsförening.db', future=True)
Session = sessionmaker(bind=engine, future=True)
session = Session()

# Vår SQLAlchemy Objekt, ORM-style
# Skapar alla kolumner samt deras namn och vilka värden de accepterar
# Likt en vanlig SQL-databas
class Members(Base):
    __tablename__ = 'Members'

    Member_ID = Column(Integer, primary_key=True, autoincrement=True)
    First_Name = Column(String)
    Last_Name = Column(String)
    Street_Address = Column(String)
    Post_Address = Column(String)
    Post_Number = Column(String)
    Paid_Fee = Column(Boolean)

# funktion för att hitta nuvarande members i databas, och spara och returnera i list[list]
# results (vår list[list] kan sedan användas för att skapa värdena i vår table i gui.py
def retrieve_members():
    results = []
    find_all_members = session.query(
        Members.Member_ID,
        Members.First_Name,
        Members.Last_Name,
        Members.Street_Address,
        Members.Post_Address,
        Members.Post_Number,
        Members.Paid_Fee).all()
    for row in find_all_members:
        results.append(list(row))
    return results

# Funktion för att skapa databasen, ska endast användas en gång per databas
def create_engine():
    Base.metadata.create_all(engine)
