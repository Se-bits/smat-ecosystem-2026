from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, auth, database

models.Base.metadata.create_all(bind=database.engine)
app = FastAPI(title="SMAT API - Unidad I")

# CONFIGURACIÓN CRÍTICA PARA SEMANA 5 (CONEXIÓN MÓVIL)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/token", tags=["Seguridad"])
def login():
    return {"access_token": auth.crear_token({"sub": "admin_fisi"}), "token_type": "bearer"}

@app.get("/estaciones/", response_model=list[schemas.Estacion], tags=["SMAT"])
def listar_estaciones(db: Session = Depends(database.get_db)):
    # Obtenemos todas las estaciones
    estaciones = db.query(models.EstacionDB).all()
    
    # Recorremos cada estación para buscar su última lectura
    for est in estaciones:
        # Buscamos la última lectura asociada a esta estación, ordenada por ID descendente
        ultima_lectura = db.query(models.LecturaDB).filter(models.LecturaDB.estacion_id == est.id).order_by(models.LecturaDB.id.desc()).first()
        
        # Si existe una lectura, se la asignamos. Si no hay ninguna aún, le ponemos 0.0
        est.lectura = ultima_lectura.valor if ultima_lectura else 0.0
        
    return estaciones

@app.post("/estaciones/", tags=["SMAT"])
def crear_estacion(estacion: schemas.EstacionCreate, db: Session = Depends(database.get_db), user=Depends(auth.validar_token)):
    nueva = models.EstacionDB(**estacion.dict())
    db.add(nueva)
    db.commit()
    return nueva

@app.put("/estaciones/{estacion_id}", tags=["SMAT"])
def actualizar_estacion(estacion_id: int, estacion_data: schemas.EstacionCreate, db: Session = Depends(database.get_db), user=Depends(auth.validar_token)):
    # Buscamos la estación en la base de datos
    estacion = db.query(models.EstacionDB).filter(models.EstacionDB.id == estacion_id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    
    # ¡Solo actualizamos estos dos campos!
    estacion.nombre = estacion_data.nombre
    estacion.ubicacion = estacion_data.ubicacion
    db.commit()
    
    return {"status": "Estación actualizada con éxito"}

@app.delete("/estaciones/{estacion_id}", tags=["SMAT"])
def eliminar_estacion(estacion_id: int, db: Session = Depends(database.get_db), user=Depends(auth.validar_token)):
    # Buscamos la estación
    estacion = db.query(models.EstacionDB).filter(models.EstacionDB.id == estacion_id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    
    # La eliminamos
    db.delete(estacion)
    db.commit()
    
    return {"status": "Estación eliminada con éxito"}

@app.post("/lecturas/", tags=["Telemetría"])
def registrar_lectura(lectura: schemas.LecturaCreate, db: Session = Depends(database.get_db), user=Depends(auth.validar_token)):
    # Reto Maestro: Validación de existencia
    estacion = db.query(models.EstacionDB).filter(models.EstacionDB.id == lectura.estacion_id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    
    nueva_lectura = models.LecturaDB(**lectura.dict())
    db.add(nueva_lectura)
    db.commit()
    return {"status": "Lectura registrada con éxito"}