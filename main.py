from fastapi import FastAPI, Path, HTTPException
import json

app = FastAPI()

def load_data():
    with open('patients.json','r') as f:
        data = json.load(f)

        return data
    
@app.get("/")
def hello():
    return {'message':'Patient Management System Api'}

@app.get('/about')
def about():
    return {'message':'A fully functinally Api to manage your patient records'}

@app.get('/view')
def view():
    data = load_data()

    return data


@app.get('/patient/{patient_id}')
def view_patients(patient_id: int = Path(...,description="ID of the patients in the DB",example='1')):
    data = load_data()

    for patient in data:
        if patient["id"] == patient_id:
            return patient

    raise HTTPException(status_code=404,detail='patients not found')