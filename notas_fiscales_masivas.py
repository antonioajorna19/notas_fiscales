import requests
import os
import threading
import time 


SITE_ID = "MLB"
ARCHIVO_SHIPMENTS = "shipments.txt" #Nombre del archivo con los shipments, ingresar con su extension.Ej: shipments.txt
FORMATO_NOTAS_FISCALES = "pdf" #pdf/xml
NOMBRE_CARPETA_DE_DESCARGA = "NOTAS_FISCALES" #Ejemplo: notas_fiscales


def obtener_info_shipments(listado_shipments:list, shipments_sin_info:list, info_shipments_id:list,
                            site_id:str) ->None:

    '''
    PRE:Recibimos en una lista los shipmets y una lista vacia donde se agregan los shipments que no se pueda obtener informacion.
    POST:Por ser un procedimiento se retorna un valor de tipo None.
    '''
    
    info_shipments = 0
    for shipment_id in listado_shipments:

        try:
            extraer_info_shipments = requests.get(f"http://internal-api.mercadolibre.com/shipments/{shipment_id}/invoice_data/all?siteId={site_id}&caller.scopes=admin&caller.id=admin")
            info_parseada = extraer_info_shipments.json()
            info_shipments_id.append((shipment_id, info_parseada[info_shipments]['sender_id'], 
                            info_parseada[info_shipments]['fiscal_key'], FORMATO_NOTAS_FISCALES))
            
            print(f"{shipment_id} - Informacion obtenida")
        except Exception:
            shipments_sin_info.append(shipment_id)

    
def obtener_listado_shipments(nombre_archivo:str) ->list:
    
    '''
    PRE:Recibe el nombre del archivo como string.
    POST:Retornamos en una lista los shipments id.    
    '''
    listado_shipments_limpios = list()

    with open(nombre_archivo,"r") as archivo:
        for shipment_id in archivo:
            listado_shipments_limpios.append(shipment_id.strip("\n"))
    
    return listado_shipments_limpios


def obtener_notas(listado_info_shipments:list, nombre_carpeta_de_descarga:str, shipments_sin_info:list) ->None:

    """
    PRE:Recibimos como lista todos los shipments ademas de el nombre de la carpeta donde se descargaran las NF de los SH.
    POST:Al ser un procedimiento, se retorna un dato de tipo None.
    """
    os.mkdir(nombre_carpeta_de_descarga)
    #os.system("cls")
    
    for shipment, sender_id, fiscal_key, type in listado_info_shipments:

        try:
            consulta = requests.get(f"https://internal-api.mercadolibre.com/shipping-tax/gateway/shipments/{shipment}/nfe/{fiscal_key}?doctype={type}&caller.id={sender_id}&caller.scopes=admin")
            with open(f"{nombre_carpeta_de_descarga}\\{shipment}.{FORMATO_NOTAS_FISCALES}","wb")as archivo:
                archivo.write(consulta.content)
                print(f"{shipment} - Nota fiscal descargada")
        except Exception:
            shipments_sin_info.append(shipment)


def mostrar_notas_no_descargadas(shipments_sin_info:list) ->None:

    '''
    PRE:Recibimos una lista de los shipments sin notas fiscales.
    POST:Al ser procedimiento retornamos un tipo de dato None.
    '''
    vacio = 0
    os.system("cls")
    
    if len(shipments_sin_info) == vacio:
        print("Todas las notas se pudieron descargar correctamente.")
    else:
        print("SHIPMETS QUE NO SE PUDO DESCARGAR SUS NOTAS FISCALES.")
    
        for shipment_id in shipments_sin_info:
            print(shipment_id)


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
    mostrar_notas_no_descargadas(shipments_sin_info)


main()
