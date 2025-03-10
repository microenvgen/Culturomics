Description
=

Generic protocol for performing PCR with the robot (using the robot's own thermocycler or an external one).

**Parameters:**

1. Internal or external PCR (external by default)
2. Number of cycles (internal only)
3. Melting temperature (internal only)

**Protocolo**

1. defrost reagents and plates
> - Template, dH2O, Bff, dNTPs, Pfw, Prv (specific ones with Ns or not). 
> - Check that there is enough of each one and enzymes (See below). 
2. Clean the deck with isopropanol. 
3. Change pipettes if necessary **(multi20 on the right)**. 
4. If the PCR is internal, put the PCR module (slots 7-11), clean the PCR silicone with 10% bleach and distilled water and **note silicone used**. 
5. Place PCR plate: 
> - Nest fullskirt in PCR module (internal). 
> - Shapire semi-skirt in slot 7 with its [adapter](https://github.com/microenvgen/OT2/blob/426f8d04e7917903d9d31d308ecbcd8541383280/custom_labware/pcr_plate_semi_skirt.md) (external). 
6. Place 20 ul tips with opentrons filter in slots 1 and 2. 
7. Make the PCR reaction mix in a Falcon 15 and mix well with vortex:


|                   |  Units     | [Initial] | [Final] |  Vol (25 µl) | Pool 109X |
|-------------------|:----------:|:---------:|:-------:|:------------:|:---------:|
| Q5 Pol            |    U/µl    |     2     |   0,02  |     0,25     |      27   |
| Q5 Reac Buffer    |      X     |     5     |    1    |     5,00     |     545   |
| dNTP              |     mM     |     10    |   0,40  |     1,00     |     109   |
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

8. Distribute the reaction mix in the first 2 columns of a full-skirt Nest PCR plate and place in slot 3 (133 ul per well). 
9. Place the plate with the template DNA in slot 4 (give it a spin for 1 min beforehand). 
10. Launch the First_PCR.py script
- First distribute 20 ul of the PCR reaction mix in the PCR plate
- Add 5 ul of the template plate to the PCR plate
- If the PCR is external, the protocol ends here. The PCR plate must be sealed and taken to the external thermocycler. The template DNA plate must also be sealed and stored appropriately. 
- If the PCR is internal, the PCR plate must be sealed and press continue to run the PCR protocol. While the PCR protocol is running, the template DNA plate and the rest of the labware can be collected.

Settings
= 

### Pipettes

Right\) p20_multi_gen2  

### Slots

1 y 2): [opentrons_96_tiprack_20ul](https://opentrons.com/products/opentrons-20-l-tips-160-racks-800-refills?sku=999-00007)  
3): Reagents [nest_96_wellplate_100ul_pcr_full_skirt](https://labware.opentrons.com/#/?loadName=nest_96_wellplate_100ul_pcr_full_skirt)  
4) ADN template [nest_96_wellplate_100ul_pcr_full_skirt](https://labware.opentrons.com/#/?loadName=nest_96_wellplate_100ul_pcr_full_skirt)  
7) PCR plate [pcr_plate_semi_skirt](https://github.com/microenvgen/OT2/blob/426f8d04e7917903d9d31d308ecbcd8541383280/custom_labware/pcr_plate_semi_skirt.md)  

or

7-8-10-11) [PCR module](https://opentrons.com/products/modules/thermocycler/) + PCR plate [nest_96_wellplate_100ul_pcr_full_skirt](https://labware.opentrons.com/nest_96_wellplate_100ul_pcr_full_skirt?category=wellPlate&manufacturer=NEST)  

CHANGELOG
=

### Notes for future changes...

A parameter could be added to define the number of columns to be made in case a complete plate is not needed.