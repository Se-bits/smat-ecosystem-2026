from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Importamos nuestros archivos locales
from app import models, schemas, crud
from app.database import engine, get_db

# ==========================================================
# CRITICAL: CREACIÓN DE LA BASE DE DATOS Y TABLAS
# Esta línea busca el archivo 'smat.db' y crea las tablas
# definidas en models.py si es que aún no existen.
# ==========================================================
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SMAT Backend Profesional",
            description="""
            API robusta para la gestión y monitoreo de desastres naturales.
            Permite la telemetría de sensores en tiempo real y el cálculo de niveles de riesgo.
            **Entidades principales:**
            * **Estaciones:** Puntos de monitoreo físico.
            * **Lecturas:** Datos capturados por sensores.
            * **Riesgos:** Análisis de criticidad basado en umbrales.
            """,
            version="1.0.0",
            terms_of_service="http://unmsm.edu.pe/terms/",
            contact={
            "name": "Soporte Técnico SMAT - FISI",
            "url": "http://fisi.unmsm.edu.pe",
            "email": "desarrollo.smat@unmsm.edu.pe",
            },
            license_info={
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
            },)

# Configuración de orígenes permitidos
origins = ["*"] # En producción, especificar dominios reales

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# ENDPOINTS REFACTORIZADOS
@app.post("/estaciones/",
            status_code=201,
            tags=["Gestión de Infraestructura"],
            summary="Registrar una nueva estación de monitoreo",
            description="Inserta una estación física (ej. río, volcán, zona sísmica) en la base de datos relacional."
            )
def crear_estacion(estacion: schemas.EstacionCreate, db: Session = Depends(get_db)):
    nueva_estacion = crud.crear_estacion(db=db, estacion=estacion)
    return {"msj": "Estación guardada en DB", "data": nueva_estacion}

@app.post("/lecturas/",
            status_code=201,
            tags=["Telemetría de Sensores"],
            summary="Recibir datos de telemetría",
            description="Recibe el valor capturado por un sensor y lo vincula a una estación existente mediante su ID."
)
def registrar_lectura(lectura: schemas.LecturaCreate, db: Session = Depends(get_db)):
    # 1. Usamos el crud para verificar si existe
    estacion = crud.get_estacion(db=db, estacion_id=lectura.estacion_id)
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no existe")
    
    # 2. Usamos el crud para guardar
    crud.crear_lectura(db=db, lectura=lectura)
    return {"status": "Lectura guardada en DB"}


@app.get("/estaciones/{id}/riesgo",
        tags=["Análisis de Riesgo"],
        summary="Evaluar nivel de peligro actual",
        description="Analiza la última lectura recibida de una estación y determina si el estado es NORMAL, ALERTA o PELIGRO."
        )
def obtener_riesgo(id: int, db: Session = Depends(get_db)):
    estacion = crud.get_estacion(db=db, estacion_id=id)
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    
    ultima_lectura = crud.get_ultima_lectura(db=db, estacion_id=id)
    if not ultima_lectura:
        return {"id": id, "nivel": "SIN DATOS", "valor": 0}
    
    valor = ultima_lectura.valor
    nivel = "PELIGRO" if valor > 20.0 else "ALERTA" if valor > 10.0 else "NORMAL"
        
    return {"id": id, "valor": valor, "nivel": nivel}

@app.get("/estaciones/{id}/historial")
async def obtener_historial(id: int, db: Session = Depends(get_db)):
    estacion = crud.get_estacion(db=db, estacion_id=id)
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    
    lecturas_db = crud.get_lecturas_by_estacion(db=db, estacion_id=id)
    promedio = sum(l.valor for l in lecturas_db) / len(lecturas_db) if lecturas_db else 0.0
        
    return {
        "estacion_id": id,
        "lecturas": lecturas_db,
        "conteo": len(lecturas_db),
        "promedio": round(promedio, 2)
    }

@app.get("/estadisticas/", tags=["Reportes y Estadísticas"], summary="Obtener reporte global")
def reporte_estadisticas(db: Session = Depends(get_db)):
    # Llamamos al crud para que haga los cálculos
    resultados = crud.obtener_estadisticas_globales(db=db)
    
    return resultados