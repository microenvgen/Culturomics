from opentrons import protocol_api

metadata = {
	'protocolName': 'Prepare Magnetic beads plate (vol < 20 ul)',
	'author': 'Alberto Rastrojo',
	"apiLevel": "2.11",
	'version': '1'
}

def run(protocol):

	# =============================================================================
	# Input data and variables
	# =============================================================================
	protocol.set_rail_lights(True)
	beads_vol = 17
	number_of_columns = 12

	rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
	columns = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
	wells = [r+c for r in rows for c in columns[:number_of_columns]]

	# =============================================================================
	# Functions
	# =============================================================================
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
	# Tips & pipette
	tips = protocol.load_labware('opentrons_96_tiprack_20ul', 1, 'tips')
	pip = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=[tips])

	# beads
	falcons = protocol.load_labware('custom_rack_6xf50_deltalab_faldon', 2, 'falcons')

	# output plate
	plate = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', 3, "plate")

	# =============================================================================
	# Calculating required beads volumen
	# =============================================================================
	required_beads_vol = (beads_vol * 8 * number_of_columns) + 500
	flash(f"### Prepara un F50 con faldón con {required_beads_vol} ul de magnetic beads y colocalo en la posición A1 del adaptador de tubos F50")

	# =============================================================================
	# Distribuiting magnetics beads
	# =============================================================================
	pip.pick_up_tip()
	pip.distribute(beads_vol,
				falcons.well('A1').bottom(z=1),
				[plate.wells_by_name()[well].bottom(z=2) for well in wells], 
				new_tip='never',
				mix_before=(2, 20), 
				disposal_volume=0, 
				blow_out=True,
				blowout_location='source well',
				)
	pip.drop_tip()
