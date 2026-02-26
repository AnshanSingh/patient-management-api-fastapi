from fastapi import FastAPI, Path, HTTPException, Query
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