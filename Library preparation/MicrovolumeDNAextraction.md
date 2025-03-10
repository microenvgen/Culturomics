1-Description
=

This script is based on the protocol described in:

> Bramucci, A. R., Focardi, A., Rinke, C., Hugenholtz, P., Tyson, G. W., Seymour, J. R., & Raina, J.-B. (2021). Microvolume DNA extraction methods for microscale amplicon and metagenomic studies. ISME Communications, 1(1), 1–5.

## Important

> Lysis time: no more than 10 minutes  
> Stop buffer adding: no more than 5 minutes after heating  

**Tip isolator preparation**: Prepare a clean empty 300ul opentrons tiprack (rinse opentrons tips rack with 0.1 N HCl and wash 3 times with MQ water). Wrap it in aluminum foil and autoclave it. When you put it in the drying oven, remove the aluminum foil so that it dries better.

> IMPORTANT: use a tip rack with tips to calibrate tip isolator, and change it before starting the protocol (there is a pause)

### Before start


**Beads plate preparation**  

In order to avoid contamination due to the manipulation of the magnetic beads we are going to prepare the beads in a plate previously using the script "prepare_MagneticBeadsPlate_highVol.py".

**Buffer verification**  

1. Thaw buffers. 
2. Do a test to verify that the pH is correct   
    i. Mix a sample (360 ul) + DTT-Lysis-Buffer (270 ul)  
    ii. Add the Stop Buffer (270 ul)  
    iii. Test the pH, it should be ~8 (test with pH strips)  
3. Clean deck and prepare all required labware  
4. Prepare Vortex for microplate  
5. **Calibrate using a toy plate in magnetic module**  

Estimated running time: 1h:53m  


### Time
5 minutes: pause to seal the plate and bring it to -80. If you are going to continue at this point, press resume run, it will fill the tip isolator and heat the thermal block. Meanwhile, seal the plate, vortex, centrifuge and store at -80 for 10 minutes.

19 minutes: Place the plate and press continue. Wait 4 minutes.

23.39: add stop buffer

30: add beads

2-Settings
= 

**Api level**

To use a tip isolater version 2.9 is required.  
Higher api levels do not seem to work (at least version 2.11).  

**Pipettes**

Right\) p300_multi_gen2  

**Slots**

1\) [Magnetic module](https://opentrons.com/modules/magnetic-module/) loaded with a [nest_96_wellplate_100ul_pcr_full_skirt](https://labware.opentrons.com/nest_96_wellplate_100ul_pcr_full_skirt?category=wellPlate&manufacturer=NEST) with 90 ul of magnetic beads (Omega Bio-Tek Mag-Bind TotalPure NGS (SKU: M1378-00))  
2\) [nest_12_reservoir_15ml](https://labware.opentrons.com/nest_12_reservoir_15ml?category=reservoir)  

>A1) 4.5 ml of Lysis buffer

>A2) 4.5 ml of Stop buffer
 
>A4) 5 ml of Elution buffer (Tris-HCl 10mM EDTA 1mM) o solo Tris

>A5-A7) 11 ml sterile Water (for tip isolator)  

>A9-A12) 11 ml 70% Ethanol  

3\) [Temperature module](https://opentrons.com/modules/temperature-module/) + [nest_96_wellplate_100ul_pcr_full_skirt](https://labware.opentrons.com/nest_96_wellplate_100ul_pcr_full_skirt?category=wellPlate&manufacturer=NEST) with samples (centrifuge plate previously)  
4\) Tip isolator(Empty rack [opentrons_96_tiprack_300ul](https://labware.opentrons.com/opentrons_96_tiprack_300ul?category=tipRack&manufacturer=Opentrons))  
5, 6, 7, 8, 9 & 11\) [opentrons_96_tiprack_300ul](https://labware.opentrons.com/opentrons_96_tiprack_300ul?category=tipRack&manufacturer=Opentrons))  
10\) Output plate ([nest_96_wellplate_100ul_pcr_full_skirt](https://labware.opentrons.com/nest_96_wellplate_100ul_pcr_full_skirt?category=wellPlate&manufacturer=NEST))

3-Deck
= 

![Deck](./MicrovolumeDNAextraction_deck.svg)


4-CHANGELOG
=

#### Notes for future changes...

### V3

Magnetic beads are no longer placed in the reservoir, but a PCR plate with the required number of beads per well must be prepared using the "prepare_MagneticBeadsPlate_highVol.py" protocol. This plate will be placed on the magnetic module. The samples, which are initially placed in the thermal module, are then placed back on the thermal block after lysis and neutralization. The robot then transfers the samples from the thermal block to the magnetic block where they will come into contact with the magnetic beads.

On the other hand, during DNA recovery after elution, the protocol has been modified to pipette at various heights to recover the maximum possible volume. 

We modified step 6: instead of incubating for 5 minutes, we mix the samples with the beads 2 times (5 repetitions of 150 ul).

### V2

We added an option to choose the number of columns to be processed by the protocol

### V1

#### Protocol

0. Put samples plate over temperature module
1. Add 27 ul of Lysis buffer to each sample (seal the plate, vortex, centrifuge and freeze)
2. Freeze plate at -80ºC for at least 10 minutes (up to 4 hours)
3. Heat samples at 55ºC for 4 minutes
4. Add 27 ul of Stop Buffer to the samples and mix (seal the plate, vortex, centrifuge and put in magnetic module)
5. Add 90 ul of magnetic beads (mix beads before, 10X-300ul) to the samples and mix (10X-150 ul). Drop tips in tip isolator to re-used then later. 
6. Incubate at RT for 5 minutes.
7. Engage magnet and incubate 5 minutes.
8. Remove supernatant (180 ul) using tips from tip isolator (drop tip in tip isolator)
9. Add 180 ul of 70% ethanol (using same tips for the whole plate) and incubate 1 minute ar RT
10. Remove supernatant (using tips from tip isolator and return them)
11. Repeat wash (steps 10 and 11)
12. Remove ethanol remains
13. Check if there are ethanol remains, remove manualy and let beads air dry for at least 10 minutes.
14. Disengage magnet, add elution buffer, mix  (20X-20 ul) and incubate for 5 minutes at RT
15. Engage magnet, wait for 5 minutes and transfer supernatant to output plate.


