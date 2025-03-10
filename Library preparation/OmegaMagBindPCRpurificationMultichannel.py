from opentrons import protocol_api
from opentrons.types import Point
import math

metadata = {
	'protocolName': 'Omega Mag-Bind PCR purification Multichannel',
	'author': 'Alberto Rastrojo',
	'apiLevel': '2.9',
	'version': '5',
}

def run(protocol: protocol_api.ProtocolContext):

	########################################################################################################
	if protocol.rail_lights_on: protocol.set_rail_lights(False)
	def cmt(msg): protocol.comment("="*100 + "\n" + msg + "\n" + "="*100)
	def shake(pipette, well, cycles):
		for _ in range(cycles):
			pipette.move_to(well.move(Point(x=-0.25)))
			pipette.move_to(well.move(Point(x=0.25)))
	########################################################################################################
	###--Protocol variables
	col_num = 12 #--Number of occupied columns in plate
	plate_type = "nest_96_wellplate_100ul_pcr_full_skirt" # pcr_plate_semi_skirt


	PCR_volume = 20 #--ul (maximum PCR volume = 90, well volume = 180 ul)
	# beads_ratio = 0.85 #--PCR_volume / beads_volume
	# beads_volume = PCR_volume * beads_ratio #--ul
	total_vol = 50 # PCR_volume + beads_volume (to be calculated by the user depending on the PCR volume and the beads volume)
	washing_volume = 150 #--ul (maximum = 150 ul)
	number_of_washes = 2 
	elution_volume = 30 #--ul
	ntips = 0

	###--Tip racks
	# tip columns required: 1xwater + col_num * (1Xadding_beads + 1Xelution + 1Xtransfer_to_output) + number_of_washes
	# tip columns required: 1 + 3*col_num + number_of_washes
	max_tip_racks = ['5', '6', '7', '8']
	required_tip_racks = math.ceil((3 * col_num + 1 + number_of_washes) / 12 )
	tip_rack_slots = max_tip_racks[:required_tip_racks]

	###--Tips & pipette
	multi_tipracks = [protocol.load_labware('opentrons_96_tiprack_300ul', slot) for slot in tip_rack_slots]
	m300 = protocol.load_instrument('p300_multi_gen2', 'right', tip_racks=multi_tipracks)

	###--Tip isolator (for tips re-use, empty rack)
	tip_isolator = protocol.load_labware('opentrons_96_tiprack_300ul', 4, 'Tip isolator')

	###--Loading module
	mag_mod = protocol.load_module('magnetic module gen2', 1)
	mag_plate = mag_mod.load_labware(plate_type)
	mag_mod.disengage()

	###--Reagents
	reagent_container = protocol.load_labware('nest_12_reservoir_15ml', 2, 'reagent reservoir')
	# beads = reagent_container.wells()[0]
	elution_buffer = reagent_container.wells()[1]
	water = [reagent_container.wells()[i] for i in [3, 4, 5]]
	ethanol_wells = [reagent_container.wells()[i] for i in [8, 9, 10, 11]]

	###--Input plate
	input_plate = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', 10 , 'input_plate')

	###--Output plate
	output_plate = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', 3 , 'output_plate')

	###--Trash
	trash = protocol.loaded_labwares[12]['A1']

	########################################################################################################
	###--Required reagent
	# total_beads_volume = ((beads_volume * col_num * 8) / 1000) + 3.4 #-- ml (mix volume is 300 ul * 8 tips > 2.4 ml to mix + 1 ml)
	total_elution_volume = ((elution_volume * col_num * 8) / 1000) + 2 #-- ml 
	water_wells_required = math.ceil(((300 * col_num * 8 ) /1000 ) / 11)
	etoh_wells_required = math.ceil((((washing_volume * col_num * 8 ) /1000 )* number_of_washes) / 11)

	cmt("#### Required reagents")
	protocol.comment("#### Change Tip isolator tick rack by an empty one.")
	# protocol.comment("#### {} ml of beads in well A1".format(total_beads_volume))
	protocol.comment("#### {} ml of elution buffer (or MQ-H2O) in well A2".format(total_elution_volume))
	protocol.comment("#### 11 ml of water in wells {}".format(["A" + str(x + 4) for x in range(water_wells_required)]))
	protocol.comment("#### 11 ml of 70\% ethanol in wells {}".format(["A" + str(x + 9) for x in range(etoh_wells_required)]))
	protocol.pause("#### Press resume to continue")

	###--Running protocol
	cmt("#### 0. Add 300 ul water to tip_isolator")
	m300.pick_up_tip()
	e = 0 #--For changing well of water
	c = 0 #--Column control to change e
	for i in range(col_num):
		if c == 4: #--Change water reservoir well every 4 columns (300 ul * 32 wells = 9.6 ml)
			e += 1
			c = 0
		m300.transfer(300, water[e].bottom(z=2), tip_isolator.columns()[i][0].bottom(z=15), new_tip='never', blow_out=True)
		c += 1
	m300.drop_tip()
	ntips += 8

	cmt("#### 1. Transfer {} ul from input to magnetic beads plate (with required beads preloded)".format(PCR_volume))
	for i in range(col_num):

		m300.pick_up_tip()
		m300.transfer(PCR_volume, input_plate.columns()[i][0].bottom(z=0.5), mag_plate.columns()[i][0].bottom(z=2), new_tip='never')
		m300.mix(10, total_vol, mag_plate.columns()[i][0].bottom(z=2))
		m300.blow_out()
		m300.drop_tip(tip_isolator.columns()[i][0])

	# # cmt("#### 1. Add {} ul of magnetic bead to samples".format(beads_volume))
	# for i in range(col_num):

	# 	m300.pick_up_tip()

	# 	#--Mixing beads (instead of using mix(), we are going to use aspire and dispence to change height in between)
	# 	m300.flow_rate.aspirate = 300
	# 	m300.flow_rate.dispense = 300
	# 	for e in range(10): #--Mixing
	# 		m300.aspirate(300, beads.bottom(z=2))
	# 		m300.dispense(300, beads.bottom(z=8))

	# 	#--Adding beads to samples
	# 	protocol.default_speed = 200 # Slow down head speed 0.5X for bead handling
	# 	m300.flow_rate.aspirate = 100
	# 	m300.flow_rate.dispense = 100
	# 	m300.transfer(beads_volume, beads.bottom(z=2), mag_plate.columns()[i][0].bottom(z=2), new_tip='never')
	# 	m300.mix(10, total_vol, mag_plate.columns()[i][0].bottom(z=2))
	# 	protocol.default_speed = 400
	# 	m300.drop_tip(tip_isolator.columns()[i][0])

	# protocol.default_speed = 400
	# ntips += 96 # re-used in next step


	# =============================================================================
	cmt("#### 2. Mezclar 2 veces las muestras con las bolitas.")
	# =============================================================================
	for _ in range(2):

		for i in range(col_num):

			m300.pick_up_tip(tip_isolator.columns()[i][0])
			m300.mix(5, PCR_volume, mag_plate.columns()[i][0].bottom(z=2))
			m300.drop_tip(tip_isolator.columns()[i][0])

	# cmt("#### 2. Incubate for 5 minutes.")
	# protocol.delay(minutes=5)

	cmt("#### 3. Engage magnet and incubate 5 minutes.")
	mag_mod.engage(10)
	protocol.delay(minutes=5)

	cmt(f"#### 4. Remove supernatant {total_vol} using tips from tip isolator.(drop tip in tip isolator)")
	m300.flow_rate.aspirate = 10
	m300.flow_rate.dispense = 100
	for i in range(col_num):
		m300.pick_up_tip(tip_isolator.columns()[i][0])
		m300.transfer(total_vol, mag_plate.columns()[i][0].bottom(z=2), trash, air_gap=20, blow_out=True, new_tip='never')
		m300.touch_tip()
		m300.drop_tip(tip_isolator.columns()[i][0])

	cmt("#### 5. Wash beads with ethanol {}X with {} ul.".format(number_of_washes, washing_volume))
	waste_etoh = 0
	ethanol_well = 0
	for _ in range(number_of_washes):

		#--Adding ethanol with a clean tips
		m300.flow_rate.aspirate = 50
		m300.flow_rate.dispense = 50
		m300.pick_up_tip()
		for i in range(col_num):
			if waste_etoh >= 8640: #--Change EtOH well every 6 columns (max washing vol)
				ethanol_well += 1
				waste_etoh = 0
			m300.transfer(washing_volume, ethanol_wells[ethanol_well].bottom(z=2), mag_plate.columns()[i][0].bottom(z=15), air_gap=20, new_tip='never')
			waste_etoh += (washing_volume * 8)
		m300.drop_tip() 
		ntips += 8 
		protocol.delay(minutes=1)

		#--Removing supernatant
		m300.flow_rate.aspirate = 10
		m300.flow_rate.dispense = 100
		for i in range(col_num):
			m300.pick_up_tip(tip_isolator.columns()[i][0])
			m300.transfer(washing_volume, mag_plate.columns()[i][0].bottom(z=2), trash, air_gap=20, blow_out=True, new_tip='never')
			m300.touch_tip()
			m300.drop_tip(tip_isolator.columns()[i][0])

	cmt("#### 6. Remove ethanol remains")
	m300.flow_rate.aspirate = 10
	m300.flow_rate.dispense = 100
	for i in range(col_num):
		m300.pick_up_tip(tip_isolator.columns()[i][0])
		m300.aspirate(50, mag_plate.columns()[i][0].bottom(z=1))
		m300.aspirate(50, mag_plate.columns()[i][0].bottom(z=0))
		m300.aspirate(50, mag_plate.columns()[i][0].bottom(z=-1))
		m300.drop_tip(tip_isolator.columns()[i][0])

	cmt("### 7. Check if there are ethanol remains, remove manualy and let beads air dry for at least 5 minutes.")
	protocol.set_rail_lights(True)
	protocol.pause("Check ethanol remains (remove manually if required).")
	protocol.set_rail_lights(False)
	protocol.delay(minutes=5)

	cmt("#### 8. Disengage magnet, add elution buffer, mix (20X-20 ul) and incubate for 5 minutes.")
	mag_mod.disengage()
	m300.flow_rate.aspirate = 100
	m300.flow_rate.dispense = 100
	for i in range(col_num): #--Adding elution
		m300.transfer(elution_volume, elution_buffer.bottom(z=2), mag_plate.columns()[i][0].bottom(z=2), mix_after=(20, 20), new_tip='always')
	protocol.delay(minutes=5) 
	ntips += 96

	cmt("#### 9. Engage magnet, wait for 5 minutes and transfer supernatant to output plate.")
	mag_mod.engage(8)
	protocol.delay(minutes=5)
	m300.flow_rate.aspirate = 5
	m300.flow_rate.dispense = 50
	for i in range(col_num):

		m300.pick_up_tip()
		m300.aspirate(elution_volume, mag_plate.columns()[i][0].bottom(z=1))
		m300.air_gap(5)
		m300.dispense(elution_volume + 10, output_plate.columns()[i][0].bottom(z=1))
		m300.blow_out(output_plate.columns()[i][0].bottom(z=3))
		shake(m300, output_plate.columns()[i][0].top(z=-2), 5)
		m300.drop_tip()

	ntips += 96
	mag_mod.disengage()
	cmt("#### END: remove output plate, seal and store.")




