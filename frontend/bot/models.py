from pydantic import BaseModel

class qr_code_query(BaseModel):
    user_id: int
    tarif: str

class qr_code_response(BaseModel):
    qr_encoded: str
    
class access_token_request(BaseModel):
    user_id: int

class access_token_response(BaseModel):
    user_id: int
    access_token: str

