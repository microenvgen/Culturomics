from opentrons import protocol_api

metadata = {
	'protocolName': 'Diluted Growth',
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

	def fill_plate(reservoir, first_r_well, plate):

		# 384 pipetting wells except B24 that will be used as negative control?
		# ["A1", "B1", "A2", "B2" ... "A23", "B23", "A24"]
		output_plate_pos = [row + str(col) for col in list(range(1,25)) for row in ["A", "B"]][:-1]

		first_r_well # Starting well of the corresponding reservoir

		# split 384 pipetting positions in chunks of 12 (6 columns)
		for i in range(0, 48, 12): 
			
			dest_wells = output_plate_pos[i:i+12]

			m300.distribute(100, 
				reservoir.wells()[first_r_well].bottom(z=1),
				[plate.wells_by_name()[well].bottom(z=2) for well in dest_wells],
				# mix_before=(5, 200),
				blow_out=False,
				disposal_volume=0,
				new_tip='never')

			first_r_well = first_r_well + 1 # every 6 columns the reservoir well must change

	# =============================================================================
	# Labware
	# =============================================================================
	# Pipettes
	tips = protocol.load_labware(tips_brand, 3)
	m300 = protocol.load_instrument('p300_multi_gen2','right', tip_racks=[tips])

	# input sample
	reservoir_1 = protocol.load_labware('nest_12_reservoir_15ml', 1)
	reservoir_2 = protocol.load_labware('nest_12_reservoir_15ml', 2)

	# Output plates
	plate_0015 = protocol.load_labware('corning_384_wellplate_112ul_flat', 7)
	plate_015  = protocol.load_labware('corning_384_wellplate_112ul_flat', 5) 
	plate_015b = protocol.load_labware('corning_384_wellplate_112ul_flat', 8) 
	plate_15   = protocol.load_labware('corning_384_wellplate_112ul_flat', 4) 

	# =============================================================================
	cmt("#### 1. Fill a 384-well plate with sample diluted to 0.015 cells/100 μL. ")
	# =============================================================================
	m300.pick_up_tip()
	fill_plate(reservoir=reservoir_1, first_r_well=0, plate=plate_0015)
	m300.drop_tip()

	# =============================================================================
	cmt("#### 2. Fill 2x384-well plates with sample diluted to 0.15 cells/100 μL. ")
	# =============================================================================
	m300.pick_up_tip()
	fill_plate(reservoir=reservoir_2, first_r_well=4, plate=plate_015)
	fill_plate(reservoir=reservoir_2, first_r_well=8, plate=plate_015b)
	m300.drop_tip()

	# =============================================================================
	cmt("#### 3. Fill a 384-well plate with sample diluted to 1.5 cells/100 μL ")
	# =============================================================================
	m300.pick_up_tip()
	fill_plate(reservoir=reservoir_1, first_r_well=8, plate=plate_15)
	m300.drop_tip()

	# =============================================================================
	cmt("#### 4. Adding negative controls")
	# =============================================================================
	m300.pick_up_tip()
	for plate in [plate_0015, plate_015, plate_015b, plate_15]:
		m300.transfer(100,
			reservoir_2.wells()[0].bottom(z=1),
			plate.wells_by_name()["B24"].bottom(z=2),
			new_tip='never')
	m300.drop_tip()

	# =============================================================================
	flash("#### END -- Seal, label, and grow")
	# =============================================================================

