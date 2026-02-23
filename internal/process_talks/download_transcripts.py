"""
Script to download transcripts.
"""

import os
import sciris as sc

host = 'https://harvard.hosted.panopto.com/Panopto/Pages/Transcription/GetCaptionVTT.ashx'
lectures = {
    # Week 1: Introduction to Infectious Disease Dynamics
    "1.1 Global Burden of Infectious Diseases": "84bffa0a-b43d-4404-b8f3-af3c00740a36",
    "1.2 Defining the Population at Risk: Demography": "8ae94e59-a535-47ce-8d83-af3b01698feb",
    "1.3 Defining the Population at Risk: Transmission Route": "a28a3e6c-5cb5-4217-8096-af3b014d3064",
    "1.4 A First Look at Basic Susceptible-Infected-Recovered Models": "75067ef8-d6bc-4d39-9345-af3b00b8a0ce",

    # Week 2: SIR Models
    "2.1 SIR Models Part 1": "09906109-9beb-4dd3-8844-af3d000b78ef",
    "2.2 SIR Models Part 2": "20afc06b-ca7c-422b-bd9e-af3b00b066cd",
    "2.3 Introduction to R0": "514d0853-5860-4780-b126-af3b013fc4b1",
    "2.4 Interventions in the Context of SIR Models": "2c6b127b-50bf-4618-89a7-af3b00ca02e4",

    # Week 3: Elaborations of SIR Models
    "3.1 Elaborations of SIR Models I": "cecef41b-edf0-43df-98f3-af3b00fd9891",
    "3.2 Elaborations of SIR Models II": "27244b79-5511-4170-8f8b-af3b0163b98a",
    "3.3 Contacts!": "e57b86e3-5924-437a-b1ce-af3c0167e3f7",
    "3.4 Calculating R0": "15e0ce22-3a26-4c6c-a977-af3b00a4a069",

    # Week 4: Vaccination
    "4.1 Introduction to the History of Vaccination": "b4908aef-68fa-479e-abdc-af3d00203ab2",
    "4.2 Incorporating Vaccination into SIR Models": "201add04-095c-430a-bae8-af3d0017f777",
    "4.3 Beyond Simple Models": "1e3c22ba-19d5-4886-8889-af3b00a14b02",
    "4.4 Case-Study: Chickenpox Vaccination and Herpes Zoster": "d71198c8-21b7-4403-a548-af3b018183e6",

    # Week 5: Parameter Estimation
    "5.1 Introduction to Parameter Estimation": "9b49cd43-8f04-4cae-ae35-af3b012f9d3f",
    "5.2 Estimating R0 Using a Simple Model": "0d69e78e-e5e3-4d9d-9673-af3b015d793a",
    "5.3 More Complex Models Part 1": "94cab2c3-fd37-41d9-9ab6-af3c0031ec55",
    "5.4 More Complex Models Part 2": "5e518971-38c9-422a-b9db-af3b00c62fdc",

    # Week 6: Vector/Water-Borne and Multi-Strain
    "6.1 Vector-Borne Infections: Malaria": "02c0e887-780b-4c8f-9f49-af3c00394cd1",
    "6.2 Water-Borne Infections: Cholera": "5d6b89c7-0bc2-41f5-bf8e-af3d0015b102",
    "6.3 Multi-Strain Pathogens": "8e88e7ff-4ac8-44f9-853b-af3b00b284ae",

    # Week 7: Surveillance and Genomics
    "7.1 Surveillance": "97251384-a30c-46ae-8614-af3b011f7b74",
    "7.2 Surveillance: Forecasting": "37bfa097-c756-4c60-9fec-af3c00526143",
    "7.3 Genomic Epidemiology": "3830e492-59e0-43de-99e5-af3b00ce0da3",
}
path = sc.thispath() / 'harvard'
os.makedirs(path, exist_ok=True)

for i, (title, arg) in enumerate(lectures.items()):
    dest = f'{path}/transcript_{i}.vtt'
    print(f'Downloading transcript {i+1} of {len(lectures)} to {dest} ({arg})...')
    cmd = f'curl -s -L "{host}?id={arg}&escape=true&language=0" -o "{dest}"'
    sc.runcommand(cmd, printinput=False, printoutput=False)

print('Done')
