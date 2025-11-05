from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "T_usuarios"
    USUARIO = Column(String(50), primary_key=True)
    CONTRASENA = Column(String(100))
    ACTIVO = Column(Integer)

class DatosGenerales(Base):
    __tablename__ = "DatosGenerales"
    DatosGeneralesKey = Column(Integer, primary_key=True)
    RFCTaxId = Column(String)
    RazonSocial = Column(String)
    Calle = Column(String)
    NumExterior = Column(String)
    NumInterior = Column(String)
    Colonia = Column(String)
    CodigoPostal = Column(String)
    Municipio = Column(String)
    Estado = Column(String)
    Pais = Column(String)
    NumeroPrograma = Column(String)
    Certificacion = Column(String)
    Licencia = Column(String)
