import fitz
import os

os.makedirs("data/raw_contracts", exist_ok=True)

contract_text = """
MODEL CONCESSION AGREEMENT FOR NATIONAL HIGHWAYS
SECTION 4: TIME FOR COMPLETION AND PENALTIES

The Authority and the Contractor agree to the following schedule of tasks:

1. The contractor shall complete the site clearance and excavation within 20 days of the commencement date. A grace period of 2 days is permitted. Delays beyond the grace period will attract a penalty of ₹20,000 per day. Quality specification: As per NHAI manual for Site Clearance.

2. The contractor shall complete sub-base course preparation within 45 days of commencement. A grace period of 5 days is permitted. Delays beyond grace period attract ₹15,000 per day penalty. Quality specification: Ensure proper compaction and leveling.

3. The bridge deck construction must be completed within 60 days. There is a grace period of 7 days allowed. Liquidated damages for delay are set at ₹25,000 per day after the grace period. Quality specification: Concrete grade M40.

4. Bituminous macadam laying shall be finalized in 30 days. Allowed grace period is 3 days. Penalty per day for delays is ₹10,000. Quality specification: Minimum thickness of 150mm.

5. Road marking and signage installation must be done within 15 days of paving completion. No grace period is allowed (0 days). The penalty per day is ₹5,000. Quality specification: Reflective thermoplastic paint.

6. Guardrail installation should be completed within 25 days. A grace period of 5 days is permitted. Any further delay will incur damages for delay at ₹8,000 per day. Quality specification: W-beam galvanized steel.
"""

doc = fitz.open()
page = doc.new_page()
# insert text
page.insert_text((50, 50), contract_text, fontsize=11)
doc.save("data/raw_contracts/nhai_sample.pdf")
print("Mock PDF generated at data/raw_contracts/nhai_sample.pdf")
