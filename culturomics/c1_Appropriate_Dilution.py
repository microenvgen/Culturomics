from opentrons import protocol_api

metadata = {
	'protocolName': 'Appropriate Dilution',
	'author': 'Silvia Talavera and Alberto Rastrojo',
	"apiLevel": "2.11",
	'version': '1'
}

def run(protocol: protocol_api.ProtocolContext):

	# =============================================================================
	# Input data and variables
	# =============================================================================
	protocol.set_rail_lights(True)
	tips_brand = "white_96_tiprack_200ul"

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
	tips = [protocol.load_labware(tips_brand, slot) for slot in [5]]
	m300 = protocol.load_instrument('p300_multi_gen2','right', tip_racks=tips)
	
	tips = protocol.load_labware(tips_brand, 8)
	s300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tips])

	# input sample
	tuberack = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_screwcap', 3)

	# Reagents
	reservoir = protocol.load_labware('nest_12_reservoir_15ml', 4)

	# Output plate
	plate = protocol.load_labware('nest_96_wellplate_200ul_flat', 2)

	# =============================================================================
	cmt("#### Step 1 -- adding 180 μL of R2A medium to each well.")
	# =============================================================================
	m300.pick_up_tip()

	m300.distribute(180,
					reservoir.wells_by_name()["A1"].bottom(z=2),
					plate.columns()[0:6],
					disposal_volume=0,
					new_tip="never")

	m300.distribute(180,
					reservoir.wells_by_name()["A2"].bottom(z=2),
					plate.columns()[6:12],
					disposal_volume=0,
					new_tip="never")

 	# =============================================================================
	cmt("#### Step 2 -- 20 μL of sample to the wells in the first column.")
	# =============================================================================
	s300.distribute(20,
					tuberack.wells_by_name()["A1"].bottom(z=2),
					plate.columns()[0],
					blow_out=False,
					disposal_volume=0)

	# =============================================================================
	cmt("#### Step 3 -- Performing serial dilution (1/10). Last column is left as negative control")
	# =============================================================================
	for i in range(10):

		if not m300.has_tip:
			m300.pick_up_tip()

		m300.transfer(20, plate.columns()[i], plate.columns()[i+1],
			mix_before=(10, 100),
			new_tip="never",
			)

		m300.drop_tip()

	# Last step is from 11 (py:10) to the trash bin
	m300.pick_up_tip()
	m300.mix(10, 100, plate.columns()[10][0])
	m300.aspirate(20, plate.columns()[10][0])
	m300.drop_tip()

	# =============================================================================
	flash("#### END -- Close plate with the lid and grow at 28ºC")
	# =============================================================================

