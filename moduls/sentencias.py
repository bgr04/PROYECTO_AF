from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "T_usuarios"
    USUARIO = Column(String(50), primary_key=True)
    CONTRASENA = Column(String(100))
    ACTIVO = Column(Integer)

class DatosGenerales(Base):
    __tablename__ = "T_datosgenerales"
    RFC = Column(String, primary_key=True)
    RAZONSOCIAL = Column(String)
    DIRECCION1 = Column(String)
    NUM_PROGRAMA = Column(String)
    CERTIFICACION1 = Column(String)
    LICENCIA = Column(String)