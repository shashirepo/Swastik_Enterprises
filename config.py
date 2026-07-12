"""
config.py — Application-wide constants for SWASTIK ENTERPRISES
"""

COMPANY_NAME  = "SWASTIK ENTERPRISES"
COMPANY_ADDR1 = "BELWARIYA, POST - MURDAHA, DISTRICT - VARANASI, UTTAR PRADESH, INDIA, PIN-221202"
COMPANY_GSTIN = "GSTIN : 09QRFPS4600L1Z2"
COMPANY_TEL   = "Tel. : +91 9936148679 (Ravindra Singh) , +91 9506114040 (Veer Singh)"
COMPANY_EMAIL = "Email : swastikenterprises8679@gmail.com"
BANK_DETAILS  = "Bank: Indian Overseas Bank  A/c No:346702000000466, IFSC :IOBA0003467  BRANCH: PARMANANDPUR, VARANASI"

TERMS = [
    "Goods once sold will not be taken back.",
    "Interest @ 18% p.a. will be charged if the payment is not made within the stipulated time.",
]

LOGO_PATH = "logo2.jpeg"
QR_PATH   = "qr_code.jpeg"
SIG_PATH  = "sign.jpg"

GST_OPTIONS  = [0.0, 5.0, 12.0, 18.0, 28.0]
COMMON_UNITS = ["Pcs.", "MTR", "KG", "Set", "Pair", "Bag", "Box", "Roll", "Ltr", "Nos.", "Mtr"]

SAMPLE_ITEMS = [
    ("SOLAR PANEL 620 WATT N-TYPE TOPCON", "85414300",  5.0,  "Pcs.", 22000.00, "ADANI",   5.0),
    ("ON GRID INVERTER 3.3 KW ",             "85044090",  1.0,  "Pcs.", 19500.00, "DEYE",   18.0),
    ("3KW APOLLO SOLAR STRUCTURE (MEDIUM 4FT X 6FT)",        "73089030",  1.0,  "Set",  13000.00, "GENERIC",18.0),
    ("ACDB & DCDB BOX",                           "85369030",  1.0,  "Set",      4750.00, "HAVELLS",18.0),
    ("POLYCAB DC WIRE 4MM",                      "85446090", 40.0,  "MTR",      0.00, "POLYCAB",18.0),
    ("POLYCAB AC WIRE 4MM",                      "85446090", 45.0,  "MTR",      0.00, "POLYCAB",18.0),
    ("EARTHING COPPER WIRE 4MM",                        "85446026", 70.0,  "MTR",      0.00, "GENERIC",18.0),
    ("INSTALLATION CHARGE",                        "85379995",  1.0,  "Set",      8000.00, "",       18.0),
    ("TRANSPORT CHARGE",                           "85389965",  1.0,  "Set",      2000.00, "",       18.0),
]
