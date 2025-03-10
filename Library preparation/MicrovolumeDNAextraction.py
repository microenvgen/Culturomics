from opentrons import protocol_api
import sys

metadata = {
	'protocolName': 'MicroVolume DNA Extraction',
	'author': 'Alberto Rastrojo',
	'apiLevel': '2.9',
	'version': '3',
}

def run(protocol: protocol_api.ProtocolContext):

	# =============================================================================
	# Input data and variables
	# =============================================================================
	protocol.set_rail_lights(True)
	col_num = 12 #--Number of occupied columns in plate
	lysis_vol = 27
	stop_vol = 27
	# beads_vol = 90
	elution_vol = 30
	wash_vol = 180
	number_of_washes = 2 # Max=2
	water_vol = 300 # for tip isolator

	# =============================================================================
	# Functions
	# =============================================================================
	def cmt(msg): 
		protocol.comment("="*100 + "\n" + msg + "\n" + "="*100)
	def flash(msg):

		light_status = 0
		if protocol.rail_lights_on: 
			light_status = 1

		for _ in range(5):
			protocol.set_rail_lights(False)
			protocol.delay(seconds=0.5)
			protocol.set_rail_lights(True)
			protocol.delay(seconds=0.5)

		protocol.comment("="*100 + "\n" + msg + "\n" + "="*100)
		protocol.pause()

		if light_status: 
			protocol.set_rail_lights(True)
		else:
			protocol.set_rail_lights(False)

	# =============================================================================
	# Labware
	# =============================================================================
	# Pipettes
	multi_tipracks = [protocol.load_labware('opentrons_96_tiprack_300ul', slot) for slot in ['11', '5', '6', '7', '8', '9']]
	m300 = protocol.load_instrument('p300_multi_gen2', 'right', tip_racks=multi_tipracks)

	# Tip isolator (for tips re-use, empty rack)
	tip_isolator = protocol.load_labware('opentrons_96_tiprack_300ul', 4, 'Tip isolator')

	# Loading modules
	mag_mod = protocol.load_module('magnetic module gen2', 1)
	mag_plate = mag_mod.load_labware('nest_96_wellplate_100ul_pcr_full_skirt')
	mag_mod.disengage()

	temp_mod = protocol.load_module('temperature module gen2', 3)
	temp_plate = temp_mod.load_labware('opentrons_96_aluminumblock_nest_wellplate_100ul')

	# Reagents
	reagent_container = protocol.load_labware('nest_12_reservoir_15ml', 2, 'reagent reservoir')
	lysis_buffer = reagent_container.wells()[0]
	stop_buffer = reagent_container.wells()[1]
	# beads = reagent_container.wells()[2]
	elution_buffer = reagent_container.wells()[3]
	water = [reagent_container.wells()[i] for i in [4, 5, 6]]
	ethanol_wells = [reagent_container.wells()[i] for i in [8, 9, 10, 11]]

	# Output plate
	output_plate = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', 10 , 'output plate')

	# Trash
	trash = protocol.loaded_labwares[12]['A1']

	# =============================================================================
	cmt("#### Required reagents")
	# =============================================================================
	total_lysis_vol = ((27 * 8 * col_num)/1000) + 3
	total_stop_vol = ((27 * 8 * col_num)/1000) + 3
	# total_beads_vol = ((90 * 8 * col_num)/1000) + 3
	total_elution_vol = ((30 * 8 * col_num)/1000) + 3
	total_ethanol_wells = (180 * 8 * col_num * number_of_washes) / (180 * 8 * 6)
	total_water_wells = (300 * 8 * col_num) / (300 * 8 * 4) # number of required well with 11 ml

	cmt(f"#### Required lysis buffer vol (ml): {total_lysis_vol}")
	cmt(f"#### Required stop buffer vol (ml): {total_stop_vol}")
	# cmt(f"#### Required beads vol (ml): {total_stop_vol}")
	cmt(f"#### Number of wells with water for tip isolator (11 ml,A5-A7): {total_water_wells}")
	cmt(f"#### Number of wells with ethanol for washes (11 ml, A9-A12): {total_ethanol_wells}")

	# =============================================================================
	flash("#### Change Tip isolator tick rack by an empty one.")
	# =============================================================================

	# =============================================================================
	cmt("#### 1. Add 27 ul of Lysis buffer to each sample")
	# =============================================================================
	for i in range(col_num):
		m300.transfer(27, lysis_buffer.bottom(z=2), temp_plate.columns()[i][0].bottom(z=2), new_tip='always') 
	# ntips += 96

	# =============================================================================
	cmt("#### 2. Freeze plate at -80ºC for at least 10 minutes (up to 4 hours)")
	flash('In 10 minutes: seal plate, vortex and centrifuge. Then, incubate at -80ºC for at least 10 minutes (up to 4 hours)\nIf you are going to continue the extraction inmediately (freezing only 10 minutes) press continue to heat the temperature module')
	# =============================================================================

	# ============================================================================================
	cmt("#### Add 300 ul water to tip_isolator while waiting...")
	# =============================================================================
	m300.pick_up_tip()
	e = 0 #--For changing well of water
	c = 0 #--Column control to change e
	for i in range(col_num):
		if c == 4: #--Change water reservoir well every 4 columns (300 ul * 32 wells = 9.6 ml)
			e += 1
			c = 0
		m300.transfer(300, water[e].bottom(z=2), tip_isolator.columns()[i][0].bottom(z=15), new_tip='never', blow_out=True)
		c += 1
	m300.drop_tip() # ntips += 8

	# =============================================================================
	cmt("#### 3. Heat samples at 55ºC for 4 minutes")
	# =============================================================================
	temp_mod.set_temperature(55)
	protocol.set_rail_lights(True)
	protocol.pause('Place samples plate on temperature module and press continue to heat the samples')
	protocol.set_rail_lights(False)
	protocol.delay(minutes=4)
	temp_mod.set_temperature(20)
	temp_mod.deactivate()

	# =============================================================================
	cmt("#### 4. Add 27 ul of Stop Buffer to the samples")
	# =============================================================================
	for i in range(col_num):
		m300.transfer(27, stop_buffer.bottom(z=2), temp_plate.columns()[i][0].bottom(z=2), new_tip='always') 
	# ntips += 96
	m300.home()
	protocol.set_rail_lights(True)
	protocol.pause('Quickly seal plate (less than 5 minutes), vortex and centrifuge. Then, put samples plate back into temperature module. Empty trash!!!')
	protocol.set_rail_lights(False) 

	# =============================================================================
	cmt("#### 5. Transfer samples from temperature module to magnetic module plate (preloaded with 90 ul of magnetic beads).")
	# =============================================================================
	for i in range(col_num):

		m300.pick_up_tip()
		m300.transfer(90, temp_plate.columns()[i][0].bottom(z=0.5), mag_plate.columns()[i][0].bottom(z=2), new_tip='never')
		m300.mix(10, 150, mag_plate.columns()[i][0].bottom(z=2))
		m300.drop_tip(tip_isolator.columns()[i][0])

	# ntips += 96 # re-used in next step

	# =============================================================================
	cmt("#### 6. Mezclar 2 veces las muestras con las bolitas.")
	# =============================================================================
	for _ in range(2):

		for i in range(col_num):

			m300.pick_up_tip(tip_isolator.columns()[i][0])
			m300.mix(5, 150, mag_plate.columns()[i][0].bottom(z=2))
			m300.drop_tip(tip_isolator.columns()[i][0])

	# =============================================================================
	cmt("#### 7. Engage magnet and incubate 5 minutes.")
	# =============================================================================
	mag_mod.engage(10)
	protocol.delay(minutes=5)

	# =============================================================================
	cmt("#### 8. Remove supernatant (180 ul) using tips from tip isolator.(drop tip in tip isolator)")
	# =============================================================================
	m300.flow_rate.aspirate = 10
	m300.flow_rate.dispense = 100
	for i in range(col_num):
		m300.pick_up_tip(tip_isolator.columns()[i][0])
		m300.transfer(180, mag_plate.columns()[i][0].bottom(z=2), trash, air_gap=20, blow_out=True, new_tip='never')
		m300.touch_tip()
		m300.drop_tip(tip_isolator.columns()[i][0])

	# =============================================================================
	cmt("#### 9. Add 180 ul of 70\% ethanol (using same tips for the whole plate) and incubate 1 minute")
	cmt("#### 10. Remove supernatant (using tips from tip isolator and return them)")
	cmt("#### 11. Repeat wash (steps 10 and 11)")
	# =============================================================================
	c = 0 #--column count to control ethanol wells
	e = 0 #--To change ethanol well from reservoir
	for _ in range(number_of_washes): #--2 washes

		# Adding ethanol with a clean tip
		m300.flow_rate.aspirate = 50
		m300.flow_rate.dispense = 50
		m300.pick_up_tip()
		for i in range(col_num):
			if c == 6: #--Change ethanol reservoir well every 6 columns (180 ul * 48 wells = 8.640 ml)
				e += 1
				c = 0
			m300.transfer(180, ethanol_wells[e].bottom(z=2), mag_plate.columns()[i][0].bottom(z=15), air_gap=20, new_tip='never')
			c += 1
		m300.drop_tip() # ntips += 8
		protocol.delay(minutes=1)

		# Removing supernatant
		m300.flow_rate.aspirate = 10
		m300.flow_rate.dispense = 100
		for i in range(col_num):
			m300.pick_up_tip(tip_isolator.columns()[i][0])
			m300.transfer(180, mag_plate.columns()[i][0].bottom(z=2), trash, air_gap=20, blow_out=True, new_tip='never')
			m300.touch_tip()
			m300.drop_tip(tip_isolator.columns()[i][0])

	# =============================================================================
	cmt("#### 12. Remove ethanol remains")
	# =============================================================================
	m300.flow_rate.aspirate = 10
	m300.flow_rate.dispense = 100
	for i in range(col_num):
		m300.pick_up_tip(tip_isolator.columns()[i][0])
		m300.aspirate(50, mag_plate.columns()[i][0].bottom(z=1))
		m300.aspirate(50, mag_plate.columns()[i][0].bottom(z=0))
		m300.aspirate(50, mag_plate.columns()[i][0].bottom(z=-1)) #--Could crash!!!
		m300.drop_tip(tip_isolator.columns()[i][0])

	# =============================================================================
	cmt("### 13. Check if there are ethanol remains, remove manualy and let beads air dry for at least 5 minutes.")
	# =============================================================================
	protocol.set_rail_lights(True)
	protocol.pause("Check ethanol remains (remove manually if required).")
	protocol.set_rail_lights(False)
	protocol.delay(minutes=5)

	# =============================================================================
	cmt("#### 14. Disengage magnet, add elution buffer, mix (20X-20 ul) and incubate for 5 minutes.")
	# =============================================================================
	mag_mod.disengage()
	protocol.delay(minutes=1)
	m300.flow_rate.aspirate = 100
	m300.flow_rate.dispense = 100
	for i in range(col_num): #--Adding elution
		m300.transfer(30, elution_buffer.bottom(z=2), mag_plate.columns()[i][0].bottom(z=2), mix_after=(20, 20), new_tip='always')
	protocol.delay(minutes=5) 
	# ntips += 96

	# =============================================================================
	cmt("#### 15. Engage magnet, wait for 5 minutes and transfer supernatant to output plate.")
	# =============================================================================
	mag_mod.engage(8)
	protocol.delay(minutes=5)
	m300.flow_rate.aspirate = 5
	m300.flow_rate.dispense = 50
	for i in range(col_num):

		m300.pick_up_tip()
		m300.aspirate(30, mag_plate.columns()[i][0].bottom(z=1))
		m300.aspirate(30, mag_plate.columns()[i][0].bottom(z=0.5))
		# m300.aspirate(30, mag_plate.columns()[i][0].bottom(z=0)) #--Could crash!!!
		m300.air_gap(10)
		m300.dispense(70, output_plate.columns()[i][0].bottom(z=1))
		m300.drop_tip()

		# m300.transfer(30, mag_plate.columns()[i][0].bottom(z=1), output_plate.columns()[i][0].bottom(z=1), new_tip='always')

	# ntips += 96
	mag_mod.disengage()

	# =============================================================================
	cmt("END: remove output plate, seal and store.")
	# =============================================================================