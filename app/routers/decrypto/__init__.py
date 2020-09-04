from fastapi import APIRouter

#from ..websockets import Networker, ConnectionManager

decrypto_router = APIRouter()

#manager = ConnectionManager(None, None, None)
#networker = Networker(manager)

#decrypto_router.include_router(
#    networker.get_router(),
#    prefix="/ws"
#)