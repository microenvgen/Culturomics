Description
=

Protocolo genérico para la realización de PCR con el robot (usando el propio termociclador del robot o un externo).  

**Parámetros:**

1. PCR interna o externa (por defecto externa)
2. Número de ciclos (sólo interna)
3. Temperatura de melting (sólo interna)

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
6. Colocar puntas 20 ul con filtro opentrons en slots 1 y 2.  
7. Hacer la mezcla de reacción de PCR en un falcon 15 y mezclar bien con vortex:

|                   |  Unidades  | [Inicial] | [Final] |  Vol (25 µl) | Pool 109X |
|-------------------|:----------:|:---------:|:-------:|:------------:|:---------:|
| Q5 Pol            |    U/µl    |     2     |   0,02  |     0,25     |      27   |
| Q5 Reac Buffer    |      X     |     5     |    1    |     5,00     |     545   |
| dNTP   (Biotools) |     mM     |     10    |   0,40  |     1,00     |     109   |
| Primer F          | µM -> pmol |     10    |   2,5   |     0,25     |      27   |
| Primer R          | µM -> pmol |     10    |   2,5   |     0,25     |      27   |
| Template          |      -     |     -     |    10   |     5,00     |     -     |
| H2O (NFW/A)       |      -     |     -     |    -    |     13,25    |    1445   |
|                   |            |           |         | Vol total--> |    2180   |

8. Repartir mezcla de reacción en las 2 primeras columnas de una placa de PCR Nest full-skirt y colocar en slot 3 (133 ul por pocillo).  
9. Colocar placa con el ADN molde ("template") en el slot 4 (darle un spin de 1 min antes).  
10. Lanzar el script Primera_PCR.py
	- Primero distribuye 20 ul de la mezcla de reacción de PCR en la placa de PCR
	- Añade 5 ul de la placa de molde a la placa de PCR
	- Si la PCR es externa el protocolo termina aquí. Hay que sellar la placa de PCR y llevarla el termociclador externo. También hay que sellar y conservar la placa de ADN molde convenientemente.  
	- Si la PCR es interna hay que sellar la placa de PCR y darle a continuar para que se ejecute el protocolo de PCR. Mientras se ejecuta el protocolo de PCR se puede recoger la placa de ADN molde y el resto de labwares.  

Settings
= 

### Pipettes

Right\) p20_multi_gen2  

### Slots

1 y 2): [opentrons_96_tiprack_20ul](https://opentrons.com/products/opentrons-20-l-tips-160-racks-800-refills?sku=999-00007)  
3): Reactivos [nest_96_wellplate_100ul_pcr_full_skirt](https://labware.opentrons.com/#/?loadName=nest_96_wellplate_100ul_pcr_full_skirt)  
4) ADN molde [nest_96_wellplate_100ul_pcr_full_skirt](https://labware.opentrons.com/#/?loadName=nest_96_wellplate_100ul_pcr_full_skirt)  
7) Placa PCR [pcr_plate_semi_skirt](https://github.com/microenvgen/OT2/blob/426f8d04e7917903d9d31d308ecbcd8541383280/custom_labware/pcr_plate_semi_skirt.md)  

o

7-8-10-11) [PCR module](https://opentrons.com/products/modules/thermocycler/) + Placa PCR [nest_96_wellplate_100ul_pcr_full_skirt](https://labware.opentrons.com/nest_96_wellplate_100ul_pcr_full_skirt?category=wellPlate&manufacturer=NEST)  

CHANGELOG
=

### Notes for future changes...

Se podría añadir un parámetro para definir el número de columnas a realizar en el caso de no necesitar una placa completa.  