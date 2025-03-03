from opentrons import protocol_api

metadata = {
	'protocolName': 'Diluted Growth',
	'author': 'Silvia Talavera and Alberto Rastrojo',
	"apiLevel": "2.11",
	'version': '2'
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
	tips = [protocol.load_labware(tips_brand, slot) for slot in [1,2]]
	m300 = protocol.load_instrument('p300_multi_gen2','right', tip_racks=tips)

	# pcr_mod
	tc_mod = protocol.load_module('thermocyclerModuleV2')
	if not tc_mod.lid_position=="open":
		tc_mod.open_lid()
	pcr_plate = tc_mod.load_labware('nest_96_wellplate_100ul_pcr_full_skirt')

	# Glycerol plate
	glycerol_plate = protocol.load_labware('pcr_strip_rack', 5)

	# Reagents
	reservoir = protocol.load_labware('nest_12_reservoir_15ml', 4)
	# A1 --> culture medium for negative controls (from previous part)
	# A3 --> Glycerol (5 ml)
	# A5 --> Lysis buffer (5 ml)
	# A7 --> Neutralization Buffer (5 ml)

	# =============================================================================
	cmt("#### 1. Adding 25 ul of glycerol to PCR strips")
	# =============================================================================
	m300.flow_rate.aspirate = 5 # 5 ul/second
	m300.flow_rate.dispense = 5
	m300.pick_up_tip()

	column = 0
	for start in [0,6]:

		m300.aspirate(150, reservoir.wells_by_name()["A3"].bottom(z=2))
		protocol.delay(seconds=15)
		m300.move_to(reservoir.wells_by_name()["A3"].top(), speed=10)
		protocol.delay(seconds=5)
		m300.move_to(glycerol_plate.columns()[start][0].top(), speed=50)

		for _ in range(6):
			m300.move_to(glycerol_plate.columns()[column][0].top(), speed=10)
			m300.move_to(glycerol_plate.columns()[column][0].bottom(z=1), speed=10)
			m300.dispense(25, glycerol_plate.columns()[column][0].bottom(z=1))
			m300.move_to(glycerol_plate.columns()[column][0].top(), speed=10)
			protocol.delay(seconds=15)
			column = column + 1

	m300.drop_tip()

	# =============================================================================
	cmt("#### 2. Transfer 25 ul from PCR plate on ThermoCycler to glycerol PCR strips")
	# =============================================================================
	m300.flow_rate.aspirate = 25 # 5 ul/second
	m300.flow_rate.dispense = 25
	for c in range(12):
		m300.transfer(25,
			pcr_plate.columns()[c][0].bottom(z=1),
			glycerol_plate.columns()[c][0].bottom(z=1),
			mix_after=(10, 50),
			new_tip="always"
			)

	# =============================================================================
	flash("#### Close PCR strips, mark all tubes properly, split and store at -80ºC. Refill tips. Empty trash.")
	# =============================================================================
	m300.reset_tipracks()

	# =============================================================================
	cmt("#### 3. Adding 20 ul of lysis buffer to PCR plate on ThermoCycler")
	# =============================================================================
	# Min volume for 300 ul multichannel is 20
	m300.transfer(20,
				reservoir.wells_by_name()["A5"].bottom(z=1),
				pcr_plate.columns(), 
				mix_after=(10, 20),
				new_tip="always"
				)

	# =============================================================================
	flash("#### Close PCR plate with aluminum seal")
	# =============================================================================

	# =============================================================================
	cmt("#### 4. Lysis bacteria by heating to 95ºC for 30 minutes")
	# =============================================================================
	tc_mod.close_lid()
	tc_mod.set_lid_temperature(105)

	profile = [	{'temperature': 95, 'hold_time_minutes': 30},
				{'temperature': 20, 'hold_time_seconds': 20}]

	tc_mod.execute_profile(steps=profile, repetitions=1, block_max_volume=50)
	tc_mod.deactivate_lid()
	tc_mod.deactivate_block()
	tc_mod.open_lid()

	# =============================================================================
	flash("#### Remove PCR plate aluminum seal")
	# =============================================================================

	# =============================================================================
	cmt("#### 5. Adding 16 ul of neutralization buffer to PCR plate on ThermoCycler")
	# =============================================================================
	# Min volume for 300 ul multichannel is 20
	m300.transfer(20,
				reservoir.wells_by_name()["A7"].bottom(z=1),
				pcr_plate.columns(), 
				mix_after=(10, 20),
				new_tip="always"
				)

	# ============================================================================
	flash("#### END: Close PCR plate with a new aluminum seal and store at -20ºC.")
	# =============================================================================

