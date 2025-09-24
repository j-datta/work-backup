from base64 import b64encode
from openai import OpenAI
import json
import time  # optional: for spacing out requests

genai_username = "jdatta"
genai_password = ""

token_string = f"{genai_username}:{genai_password}"
token_bytes = b64encode(token_string.encode())

client = OpenAI(
    api_key="",
    default_headers={"Authorization": f"Basic {token_bytes.decode()}"},
    base_url=""
)

base_prompt = '''
You are a doctor with 30 years of experience in writing medical discharge letters. 
Your task is to generate synthetic discharge summaries in a MIMIC-like JSONL format, ensuring they resemble real-world clinical records.
Ensure to generate summaries for patients from diverse age groups, including children, young adults, middle-aged, and elderly patients. 
Ensure an equal distribution of male and female patients to maintain demographic balance.
Using the exact format and style from the example provided below, generate a synthetic discharge summary:

Example:
{"hadm_id":20000750,"radiology_text":"INDICATION:  Postoperative views of the cervical spine\n\nCOMPARISON:  Prior from ___\n\nFINDINGS: \n\nLateral views of the cervical spine provided.  There is both anterior and\nposterior spinal fusion which appears to involve C3, C4, C5 anteriorly with\nanterior plate, vertebral body screws and disc spacers spanning the segment. \nPosteriorly fusion rods and screws are seen extending from C3, C4, C5, C6, C7\nthrough T1.  The alignment from C1 through C4 is preserved.  Inferior to this\nlevel, lima cannot be reliably assessed.\n\nIMPRESSION: \n\nAs above.\n","discharge_instructions":"Weigh yourself every morning, call MD if weight goes up more \nthan 3 lbs.\n\n \n\nPosterior Cervical Fusion\n\nYou have undergone the following operation: Posterior Cervical \nDecompression and Fusion\n\nImmediately after the operation:\n\n                Activity:You should not lift anything greater \nthan 10 lbs for 2 weeks.You will be more comfortable if you do \nnot sit in a car or chair for more than~45 minutes without \ngetting up and walking around.\n\n                Rehabilitation/ Physical ___ times a \nday you should go for a walk for ___ minutes as part of your \nrecovery.You can walk as much as you can tolerate.Limit any kind \nof lifting. \n\n                Cervical Collar / Neck Brace:You need to wear \nthe brace at all times until your follow-up appointment which \nshould be in 2 weeks.You may remove the collar to take a \nshower.Limit your motion of your neck while the collar is \noff.Place the collar back on your neck immediately after the \nshower.\n\n                Wound Care:Remove the dressing in 2 days.If the \nincision is draining cover it with a new sterile dressing.If it \nis dry then you can leave the incision open to the air.Once the \nincision is completely dry (usually ___ days after the \noperation) you may take a shower.Do not soak the incision in a \nbath or pool.If the incision starts draining at anytime after \nsurgery,do not get the incision wet.Call the office at that \ntime.If you have an incision on your hip please follow the same \ninstructions in terms of wound care.\n\n                You should resume taking your normal home \nmedications\n\n                You have also been given Additional Medications \nto control your pain.Please allow 72 hours for refill of \nnarcotic prescriptions, so please plan ahead.You can either have \nthem mailed to your home or pick them up at the clinic located \nin ___ office.We are not allowed to call in narcotic \nprescriptions (oxycontin,oxycodone,percocet) to the pharmacy.In \naddition,we are only allowed to write for pain medications for \n90 days from the date of surgery.\n\n                Follow up:\n\n___                Please Call the office and make an \nappointment for 2 weeks after the day of your operation if this \nhas not been done already.\n\n___                At the 2-week visit we will check your \nincision,take baseline x rays and answer any questions.\n\n \n\nPlease call the office if you have a fever>101.5 degrees \nFahrenheit,drainage from your wound,or have any questions.\nPhysical Therapy:\nAmbulate as tolerated- soft collar for comfort\nTreatments Frequency:\nincision clean and dry\nStaples in place","brief_hospital_course":"Patient was admitted to Orthopedic Spine Service on ___ for \nfurther management.  He was preoped for possible I&D.  \nCOnsequently, on ___ he underwent the above stated \nprocedure.  Please review dictated operative report for details. \nPatient was extubated without incident and was transferred to \nPACU then floor in stable condition.  \n\n \n\nDuring the patient's course ___ were used for \npostoperative DVT prophylaxis.  Intravenous antibiotics were \ncontinued for 24hrs postop per standard protocol. Initial postop \npain was controlled with oral and IV pain medication. Diet was \nadvanced as tolerated. Hospital course was otherwise \nunremarkable.  He was started on Keflex for 10 days.  His hand \nweakness remained unchanged. \n\n \n\nNow, Day of Discharge, patient is afebrile, VSS, and neuro \nintact with improvement of radiculopathy. Patient tolerated a \ngood oral diet and pain was controlled on oral pain medications. \nPatient ambulated independently. Patient's wound is clean, dry \nand intact. Patient noted improvement in radicular pain. Patient \nis set for discharge to home in stable condition."}
Your output should be in JSONL format. Every time Generate data with different hadm_id.
Important: Do not use pretty-printing. Each JSON object should be in a single line.
'''

for i in range(1, 101):  # 1 to 100
    prompt_text = base_prompt + f"\n\n[SESSION_RUN: {i}]"

    response = client.chat.completions.create(
        model="Llama-3.1-70B-Instruct",
        messages=[
            {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
            {"role": "user", "content": prompt_text}
        ],
        max_tokens=2048,
        temperature=0.7,
        top_p=0.6,
        extra_headers={"X-Request-ID": f"discharge-{i:05}"},
        stream=False
    )

    chat_response = response.choices[0].message.content
    lines = chat_response.strip().split("\n")

    output_file_path = f"/home/IAIS/jdatta/mimic_syntheticData/english/summaries_{i}.jsonl"

    with open(output_file_path, "w", encoding="utf-8") as f:
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                parsed_json = json.loads(line)
                f.write(json.dumps(parsed_json, ensure_ascii=False) + "\n")
            except json.JSONDecodeError:
                print(f"[Run {i}] Skipping invalid JSON line: {line}")

    print(f"[✓] Generated: {output_file_path}")
    # Optional: Avoid hitting API limits too quickly
    time.sleep(3)
