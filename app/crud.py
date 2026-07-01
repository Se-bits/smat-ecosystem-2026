from sqlalchemy.orm import Session
from app import models
from app import schemas
from sqlalchemy import func

# --- OPERACIONES DE ESTACIONES ---

def get_estacion(db: Session, estacion_id: int):
    return db.query(models.EstacionDB).filter(models.EstacionDB.id == estacion_id).first()

def crear_estacion(db: Session, estacion: schemas.EstacionCreate):
    nueva_estacion = models.EstacionDB(id=estacion.id, nombre=estacion.nombre, ubicacion=estacion.ubicacion)
    db.add(nueva_estacion)
    db.commit()
    db.refresh(nueva_estacion)
    return nueva_estacion


# --- OPERACIONES DE LECTURAS ---

def crear_lectura(db: Session, lectura: schemas.LecturaCreate):
    nueva_lectura = models.LecturaDB(valor=lectura.valor, estacion_id=lectura.estacion_id)
    db.add(nueva_lectura)
    db.commit()
    db.refresh(nueva_lectura)
    return nueva_lectura

def get_ultima_lectura(db: Session, estacion_id: int):
    return db.query(models.LecturaDB)\
             .filter(models.LecturaDB.estacion_id == estacion_id)\
             .order_by(models.LecturaDB.id.desc())\
             .first()

def get_lecturas_by_estacion(db: Session, estacion_id: int):
    return db.query(models.LecturaDB).filter(models.LecturaDB.estacion_id == estacion_id).all()

def obtener_estadisticas_globales(db: Session):
    # 1. Total de estaciones (usando función agregada COUNT)
    total_estaciones = db.query(func.count(models.EstacionDB.id)).scalar()
    
    # 2. Cantidad total de lecturas (usando función agregada COUNT)
    total_lecturas = db.query(func.count(models.LecturaDB.id)).scalar()
    
    # 3. Punto crítico máximo
    # Ordenamos de mayor a menor (desc) y tomamos el primero para saber qué estación fue
    punto_critico = db.query(models.LecturaDB).order_by(models.LecturaDB.valor.desc()).first()

    if punto_critico:
        estacion_max_id = punto_critico.estacion_id
        valor_maximo = punto_critico.valor
    else:
        estacion_max_id = None
        valor_maximo = 0.0

    # Retornamos un diccionario con todo listo
    return {
        "total_estaciones": total_estaciones or 0,
        "total_lecturas_procesadas": total_lecturas or 0,
        "punto_critico_maximo": {
            "estacion_id": estacion_max_id,
            "valor_lectura": valor_maximo
        }
    }