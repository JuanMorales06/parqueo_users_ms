from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from config.database import engine, Base, Session
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from models.aprendices import Aprendices as AprendizModel
from schemas.aprendices import Aprendices, ChangeStatusRequest
from models.aprendices import EstadoAprendiz
from models.vehicles import Motocicleta as MotocicletaModel
from models.vehicles import Bicicleta as BicicletaModel


aprendices_router = APIRouter()


@aprendices_router.get("/api/v1/aprendices-all", tags=['Aprendices'])
def get_user_all():
    db = Session()  
    aprendinces = db.query(AprendizModel).all()
    aprendices_with_roll = []
    for user in aprendinces:
        user_dict = user.__dict__
        user_dict['roll'] = "aprendiz"
        aprendices_with_roll.append(user_dict)
    return JSONResponse(status_code=200, content=jsonable_encoder(aprendices_with_roll))


@aprendices_router.post("/api/v1/aprendiz-registration", tags=['Aprendices'])
async def create_aprendiz(aprendices: Aprendices):
    
    db = Session()
    aprendiz_exist = db.query(AprendizModel).filter(AprendizModel.document == aprendices.document).first()
    if aprendiz_exist:
            raise HTTPException(status_code=400, detail="El documento ya existe") 
    try:
        finish_date = datetime.strptime(aprendices.finish_date, "%Y-%m-%d")        
        status_default = 1
        aprendices.document = int(aprendices.document)
        aprendices.ficha = int(aprendices.ficha)           
        new_aprendiz = AprendizModel(
            name=aprendices.name,
            last_name=aprendices.last_name,
            document=aprendices.document,
            ficha=aprendices.ficha,
            photo=aprendices.photo,
            email=aprendices.email,     
            finish_date=finish_date,
            state_id=status_default
        )
        db.add(new_aprendiz)
        db.commit()
        return {"message": "El aprendiz fue registrado exitosamente"}
    except Exception:
        raise HTTPException(status_code=500, detail=f"Error en la operación")


@aprendices_router.get("/api/v1/aprendices/id/document/{id}", tags=['Aprendices'])
def get_aprendiz_by_id(id: int):
    db = Session()
    aprendiz_by_id = db.query(AprendizModel).filter(AprendizModel.id == id).first()
    return JSONResponse(status_code=200, content=jsonable_encoder(aprendiz_by_id))


@aprendices_router.get("/api/v1/aprendices/{document}", tags=['Aprendices'])
def get_aprendiz_by_document(document: int):
    db = Session()
    aprendiz_by_document = db.query(AprendizModel).filter(AprendizModel.document == document).first()
    if aprendiz_by_document is None:
        raise HTTPException(status_code=404, detail="El documento no fue encontrado")   
    return JSONResponse(status_code=200, content=jsonable_encoder(aprendiz_by_document))


@aprendices_router.get("/api/v1/aprendiz-status/{document}", tags=['Estatus de Aprendices'])
def get_aprendiz_satus_by_document(document: int):
    db = Session()
    aprendiz = db.query(AprendizModel).filter(AprendizModel.document == document).first()
    if aprendiz is None:
        raise HTTPException(status_code=404, detail="El documento no fue encontrado")   
    
    aprendiz_status_id = db.query(AprendizModel).filter(AprendizModel.document == document).first().state_id
    status = db.query(EstadoAprendiz).filter(EstadoAprendiz.id == aprendiz_status_id).first().estado
    return JSONResponse(status_code=200, content=jsonable_encoder(status))



@aprendices_router.get("/api/v1/aprendiz-statu", tags=['Estatus de Aprendices'])
def get_aprendiz_satus():
    db = Session()
    aprendices = db.query(AprendizModel).all()
    vehicles =  db.query(MotocicletaModel).all()
    
    aprendices_dict = {aprendiz.document: aprendiz for aprendiz in aprendices}
    
    
    for vehicle in vehicles:
        if vehicle.user_document in aprendices_dict:
            aprendiz = aprendices_dict[vehicle.user_document]
            aprendiz.vehicle = vehicle
    
    aprendices_combined = list(aprendices_dict.values())
    
    # if aprendiz is None:
    #     raise HTTPException(status_code=404, detail="El documento no fue encontrado")   
    

    return JSONResponse(status_code=200, content=jsonable_encoder(aprendices_combined))


@aprendices_router.put("/api/v1/aprendiz-change-status", tags=['cambio de Estatus de Aprendices'])
def change_aprendiz_satus(req: ChangeStatusRequest):
    document = int(req.document)
    db = Session()
    aprendiz = db.query(AprendizModel).filter(AprendizModel.document == document).first()
    if aprendiz is None:
        raise HTTPException(status_code=404, detail="El documento no fue encontrado")   
    aprendiz.state_id = int(req.state_id)
    db.commit()
    
    return JSONResponse(status_code=200, content=jsonable_encoder({"message": "El estado del aprendiz fue actualizado correctamente"}))