from fastapi import FastAPI, Path, HTTPException, Query
from pydantic import BaseModel, Field, computed_field
from fastapi.responses import JSONResponse
from typing import Annotated, Literal, Optional
import json

app = FastAPI()

class Patient(BaseModel):
    id: Annotated[int,Field(..., description='Id of the patient', examples=[1])]   # changed str → int
    name: Annotated[str,Field(..., description="Name of the patient")]
    city: Annotated[str,Field(..., description="Enter the city where the patient is living")]
    age: Annotated[int, Field(..., gt=0, lt=120, description="Age of the patient")]
    gender: Annotated[Literal['male','female','others'],Field(...,description='Gender of the patient')]
    height: float
    weight: float

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return 'underweight'
        elif self.bmi < 25:
            return 'normal'
        elif self.bmi < 30:
            return 'overweight'   # fixed
        else:
            return 'obese'

class PatientUpdate(BaseModel):
     name: Annotated[Optional[str],Field(default=None)]
     city: Annotated[Optional[str],Field(default=None)]
     age: Annotated[Optional[int], Field(default=None, gt=0,)]
     gender: Annotated[Optional[Literal['male','female','others']],Field(default=None)]
     height: Annotated[Optional[float],Field(default=None,gt=0)]
     weight: Annotated[Optional[float],Field(default=None,gt=0)]


# moved outside class
def load_data():
    with open('2_patients.json','r') as f:
        data = json.load(f)
    return data
        

def save_data(data):   # added parameter
    with open('2_patients.json','w') as f:
        json.dump(data,f,indent=4)


@app.get("/")
def hello():
    return {'message':'Patient Management System Api'}

@app.get('/about')
def about():
    return {'message':'A fully functionally Api to manage your patient records'}

@app.get('/view')
def view():
    data = load_data()
    return data


@app.get('/patient/{patient_id}')
def view_patients(patient_id: int = Path(...,description="ID of the patients in the DB",example=1)):
    data = load_data()

    for patient in data:
        if patient["id"] == patient_id:
            return patient

    raise HTTPException(status_code=404,detail='patients not found')


@app.get('/sort')
def sort_patient(
    sort_by: str = Query(..., description='sort on the basis of height, weight or bmi'),
    order: str = Query('asc', description='sort in ascending or descending order')
):

    valid_fields = ['height', 'weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(
            status_code=400,
            detail=f'Invalid field select from {valid_fields}'
        )

    if order not in ['asc', 'desc']:
        raise HTTPException(
            status_code=400,
            detail='Invalid order select between asc and desc'
        )

    data = load_data()

    sort_order = True if order == 'desc' else False

    sorted_data = sorted(
        data,
        key=lambda x: x.get(sort_by, 0),
        reverse=sort_order
    )

    return sorted_data


@app.post('/create')
def create_patient(patient: Patient):

    data = load_data()

    for p in data:   # fixed duplicate check
        if p["id"] == patient.id:
            raise HTTPException(status_code=400, detail='patient already exist')

    data.append(patient.model_dump())   # fixed model_dump_json

    save_data(data)

    return JSONResponse(
        status_code=201,
        content={"message":"patient created successfully"}   # fixed dictionary
    )

@app.put('/edit/{patient_id}')
def update_patient(patient_id: int, patient_update: PatientUpdate):
    data = load_data()

    for i, patient in enumerate(data):
        if patient["id"] == patient_id:

            update_data = patient_update.model_dump(exclude_unset=True)

            # update fields
            for key, value in update_data.items():
                patient[key] = value

            # recalculate BMI + verdict using Pydantic
            updated_patient = Patient(**patient)

            # save updated patient
            data[i] = updated_patient.model_dump()

            save_data(data)

            return JSONResponse(
                status_code=200,
                content={"message": "patient updated successfully"}
            )

    raise HTTPException(status_code=404, detail="patient not found")