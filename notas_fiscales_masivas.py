import requests
import os
import threading
import time 
import shutil




SITE_ID = "MLB"
ARCHIVO_SHIPMENTS = "input.txt" #Nombre del archivo con los shipments, ingresar con su extension.Ej: shipments.txt
FORMATO_NOTAS_FISCALES = "pdf" #pdf/xml
NOMBRE_CARPETA_DE_DESCARGA = "SSHP-296141" #Ejemplo: notas_fiscales



def obtener_shipments_de_hus(listado_hus:list, listado_shipments:list) ->None:
    """
    PRE:Recibimos el listado de ctes y el de los shipments(vacio), buscamos obtener los shipments de estos ctes.
    POST:Una vez agregados los shipments de cada cte, se retorna un valor None, dado que es un procedimiento.
    """
    
    for hu_id in listado_hus:
        informacion_hu = requests.get(f"http://internal-api.mercadolibre.com/tms-mlb/outbounds/{hu_id}/internal")
        data_hu_formateada = informacion_hu.json()
        data_shipment = data_hu_formateada["shipments"]

        for shipment_id in data_shipment:
            listado_shipments.append(shipment_id["id"])
    
    print("Obteniendo shipments.")

def obtener_info_shipments(listado_shipments:list, shipments_sin_info:list, info_shipments_id:list,
                            site_id:str) ->None:

    '''
    PRE:Recibimos en una lista los shipmets y una lista vacia donde se agregan los shipments que no se pueda obtener informacion.
    POST:Por ser un procedimiento se retorna un valor de tipo None.
    '''
    
    info_shipments = 0
    prueba = len(listado_shipments)
    print(prueba)
    for shipment_id in listado_shipments:

        try:
            
            extraer_info_shipments = requests.get(f"http://internal-api.mercadolibre.com/shipments/{shipment_id}/invoice_data/all?siteId={site_id}&caller.scopes=admin&caller.id=admin")
            info_parseada = extraer_info_shipments.json()
            info_shipments_id.append((shipment_id, info_parseada[info_shipments]['sender_id'], 
                            info_parseada[info_shipments]['fiscal_key'], FORMATO_NOTAS_FISCALES))
        
            print(f"{shipment_id} - Informacion obtenida")
        except Exception:
            shipments_sin_info.append(shipment_id)

def Validating_HU(data:str):

    '''
    PRE:Recibimos el Dato, contamos las cantidades de digitos para identificar HU'S
    POST: 
    '''
    text = [char for char in data]

    if len(text) < 15 :
        IsHU = False
    else:
        IsHU = True
    
    return IsHU
    
def obtener_listado_shipments(nombre_archivo:str) ->list:
    
    '''
    PRE:Recibe el nombre del archivo como string.
    POST:Retornamos en una lista los shipments id.    
    '''
    listado_shipments_limpios = list()
    Listado_HU = list()

    with open(nombre_archivo,"r") as archivo:
        
        for shipment_id in archivo:

            if not Validating_HU(shipment_id.strip("\n")):
              listado_shipments_limpios.append(shipment_id.strip("\n"))
              
            else :
                Listado_HU.append(shipment_id.strip("\n"))

        
        if len(Listado_HU) != 0:
            obtener_shipments_de_hus(Listado_HU,listado_shipments_limpios)
    
    return listado_shipments_limpios


def obtener_notas(listado_info_shipments:list, nombre_carpeta_de_descarga:str, shipments_sin_info:list) ->None:

    """
    PRE:Recibimos como lista todos los shipments ademas de el nombre de la carpeta donde se descargaran las NF de los SH.
    POST:Al ser un procedimiento, se retorna un dato de tipo None.
    """
    os.mkdir(nombre_carpeta_de_descarga)
    #os.system("cls")
    print(len(listado_info_shipments))
    for shipment_id, sender_id, fiscal_key, type in listado_info_shipments:

        try:
           
            consulta = requests.get(f"https://internal-api.mercadolibre.com/shipping-tax/gateway/shipments/{shipment_id}/nfe/{fiscal_key}?doctype={type}&caller.id={sender_id}&caller.scopes=admin")
            with open(f"{nombre_carpeta_de_descarga}\\{shipment_id}.{FORMATO_NOTAS_FISCALES}","wb")as archivo:
                archivo.write(consulta.content)
                print(f"{shipment_id} - Nota fiscal descargada")
        except Exception:
            shipments_sin_info.append(shipment_id)


def mostrar_notas_no_descargadas(shipments_sin_info:list) ->None:

    '''
    PRE:Recibimos una lista de los shipments sin notas fiscales.
    POST:Al ser procedimiento retornamos un tipo de dato None.
    '''
    vacio = 0
    # os.system("cls")
    
    if len(shipments_sin_info) == vacio:
        print("Todas las notas se pudieron descargar correctamente.")
    else:
        print("SHIPMETS QUE NO SE PUDO DESCARGAR SUS NOTAS FISCALES.")
    
        for shipment_id in shipments_sin_info:
            print(shipment_id)


def comprimir_carpeta(nombre_carpeta:str) ->None:
    """
    PRE:Se recibe el nombre de la carpeta a comprimir.
    POST:Una vez comprimida, se retorna un dato de tipo None, esto debido a ser un procedimiento.
    """

    shutil.make_archive(nombre_carpeta,"zip",nombre_carpeta)



def main():

    
    info_shipments = list()
    shipments_sin_info = list()
    listado_shipments = obtener_listado_shipments(ARCHIVO_SHIPMENTS)
    
    hilo_1 = threading.Thread(target=obtener_info_shipments, args=(listado_shipments,shipments_sin_info, info_shipments, SITE_ID))
    hilo_2 = threading.Thread(target=obtener_notas, args=(info_shipments,NOMBRE_CARPETA_DE_DESCARGA, shipments_sin_info))
    
    hilo_1.start() 
    time.sleep(0.8)

    hilo_2.start()
    hilo_2.join()
    comprimir_carpeta(NOMBRE_CARPETA_DE_DESCARGA)
    mostrar_notas_no_descargadas(shipments_sin_info)
    


main()
