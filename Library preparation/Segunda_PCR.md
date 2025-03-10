Description
=

Protocolo genérico para la realización de la segunda PCR con el robot (usando el propio termociclador del robot o un externo).  

**Parámetros:**

1. PCR interna o externa (por defecto externa)
2. Dilución 1/10 del ADN modle (por defecto no)
3. Tipo de placa del ADN molde (NEST fullskirt o Shapire semi-skirt, por defecto NEST)
4. Número de ciclos (sólo interna)
5. Temperatura de melting (sólo interna)

**Protocolo**

1. Sacar a descongelar reactivos y placas
> - Template, dH2O, Bff, dNTPs, Pfw, Prv (los específicos que sean con Ns o no).  
> - Comprobar que hay suficiente de cada uno y enzimas (Ver abajo).  
2. Limpiar el deck con isopropanol.  
3. Cambiar las pipetas si es necesario **(multi20 a la derecha)**.  
4. Si la PCR es interna poner el módulo de PCR (slots 7-11), limpiar la silicona de la PCR con lejía 10% y agua destilada y **anotar uso silicona**.
5. Colocar placa PCR: 
> - Nest fullskirt en módulo PCR (interna).  
> - Shapire semi-skirt en slot 7 con su [adaptador](https://github.com/microenvgen/OT2/blob/426f8d04e7917903d9d31d308ecbcd8541383280/custom_labware/pcr_plate_semi_skirt.md) (externa).  
6. Colocar puntas 20 ul con filtro opentrons en slots 1, 2 y 9.  
7. Hacer la mezcla de reacción de PCR en un falcon 15 y mezclar bien con vortex:

|                   |  Unidades  | [Inicial] | [Final] |  Vol (25 µl) | Pool 109X |
|-------------------|:----------:|:---------:|:-------:|:------------:|:---------:|
| Q5 Pol            |    U/µl    |     2     |   0,02  |     0,25     |   27,25   |
| Q5 Reac Buffer    |      X     |     5     |    1    |     5,00     |   545,00  |
| dNTP   (Biotools) |     mM     |     10    |   0,40  |     1,00     |   109,00  |
| Primers   P5&P7*  | µM -> pmol |     6     |  12,00  |     2,00     |     -     |
| Template          |      -     |     -     |    10   |     3,00     |     -     |
| H2O (NFW/A)       |      -     |     -     |    -    |     13,75    |  1498,75  |
|                   |            |           |         | Vol total--> |  2180,00  |
*Los pone el robot, aunque hay que tenerlos en cuenta aquí para preparar bien la mix con las concentraciones adecuadas

8. Repartir mezcla de reacción en las 2 primeras columnas de una placa de PCR Nest full-skirt y colocar en slot 3 (133 ul por pocillo).  
9. Si se requiere dilución del ADN molde colocar placa placa Saphire semi-skirt con su adaptador en slot 5 y añadir 140 ul de agua limpia (NFW) en las columans 5 y 6 de la placa de reactivos del slot 3.  
10. Colocar placa con el ADN molde ("template") en el slot 4 (darle un spin de 1 min antes).  
11. Colocar placa de Barcodes en el slot 6 (anotar que mix se va a usar). 
> Al finalizar la PCR se pueden conservar los restos de los barcodes a 4ºC rotulando la placa con el nombre y fecha del experimento actual de manera que si hay que repetir PCR de este mismo experimento podemos reutilizar la misma placa. Una vez que el experimento esté completo se debe tirar los restos de esos barcodes.  
> Para repetir esta segunda PCR (y la primera) para algunas muestras se puede usar el script "de_9_a_1.py" que va a agrupar las muestras que no han salido de esta PCR y de otras, tanto en las muestras, como en las placas de barcodes, de manera que los barcodes estarán en las posiciones requeridas para usarlos con las muestras que no salieron.  
11. Lanzar el script Primera_PCR.py
	- Si se ha seleccionado dilución, realiza la dilución.  
	- Luego distribuye 20 ul de la mezcla de reacción de PCR en la placa de PCR.  
	- Añade 3 ul de la placa de molde (diluida o no, según los parámetros seleccionadoss) a la placa de PCR.  
	- Añade 3 ul de la placa de los barcodes.  
	- Si la PCR es externa el protocolo termina aquí. Hay que sellar la placa de PCR y llevarla el termociclador externo. También hay que sellar y conservar la placa de ADN molde convenientemente.  
	- Si la PCR es interna hay que sellar la placa de PCR y darle a continuar para que se ejecute el protocolo de PCR. Mientras se ejecuta el protocolo de PCR se puede recoger la placa de ADN molde y el resto de labwares.  

Settings
= 

### Pipettes

Right\) p20_multi_gen2  

### Slots

1, 2 y 9): [opentrons_96_tiprack_20ul](https://opentrons.com/products/opentrons-20-l-tips-160-racks-800-refills?sku=999-00007)  
3): Reactivos [nest_96_wellplate_100ul_pcr_full_skirt](https://labware.opentrons.com/#/?loadName=nest_96_wellplate_100ul_pcr_full_skirt)  
4) ADN molde [nest_96_wellplate_100ul_pcr_full_skirt](https://labware.opentrons.com/#/?loadName=nest_96_wellplate_100ul_pcr_full_skirt)  
5) Si se requiere dilución: ADN molde diluido [pcr_plate_semi_skirt](https://github.com/microenvgen/OT2/blob/426f8d04e7917903d9d31d308ecbcd8541383280/custom_labware/pcr_plate_semi_skirt.md)  
6) Placa Barcodes [nest_96_wellplate_100ul_pcr_full_skirt](https://labware.opentrons.com/#/?loadName=nest_96_wellplate_100ul_pcr_full_skirt)  
7) Placa PCR [pcr_plate_semi_skirt](https://github.com/microenvgen/OT2/blob/426f8d04e7917903d9d31d308ecbcd8541383280/custom_labware/pcr_plate_semi_skirt.md)  

o

7-8-10-11) [PCR module](https://opentrons.com/products/modules/thermocycler/) + Placa PCR [nest_96_wellplate_100ul_pcr_full_skirt](https://labware.opentrons.com/nest_96_wellplate_100ul_pcr_full_skirt?category=wellPlate&manufacturer=NEST)  

CHANGELOG
=

### Notes for future changes...

Se podría añadir un parámetro para definir el número de columnas a realizar en el caso de no necesitar una placa completa.  