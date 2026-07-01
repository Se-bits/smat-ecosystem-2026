from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class EstacionDB(Base):
    __tablename__ = "estaciones"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True)
    ubicacion = Column(String)
    lecturas = relationship("LecturaDB", back_populates="estacion")

class LecturaDB(Base):
    __tablename__ = "lecturas"
    id = Column(Integer, primary_key=True, index=True)
    valor = Column(Float)
    fecha = Column(DateTime, default=datetime.utcnow)
    estacion_id = Column(Integer, ForeignKey("estaciones.id"))
    estacion = relationship("EstacionDB", back_populates="lecturas")