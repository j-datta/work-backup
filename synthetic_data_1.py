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
{"hadm_id":20000254,"radiology_text":"EXAMINATION:\nChest:  Frontal and lateral views\n\nINDICATION:  History: ___ with hx pancreatitis now with burning epigastric\npain radiating to back  // please assess for etiologies of abdominal pain\n\nTECHNIQUE:  Chest:  Frontal and Lateral\n\nCOMPARISON:  None.\n\nFINDINGS: \n\nThe lungs are clear without focal consolidation.  No pleural effusion or\npneumothorax is seen. The cardiac and mediastinal silhouettes are\nunremarkable.  No evidence of free air is seen beneath the diaphragm.\n\nIMPRESSION: \n\nNo acute cardiopulmonary process.\n\\BEGIN NEW REPORT:___\nINDICATION:  Evaluate for obstruction in a ___ woman with abdominal\npain and constipation.\n\nTECHNIQUE:  Frontal supine and upright abdominal radiographs were obtained.\n\nCOMPARISON:  CT abdomen/pelvis from ___.\n\nFINDINGS: \n\nThere are no abnormally dilated loops of large or small bowel.  A large fecal\nburden is noted.\nThere is no free intraperitoneal air.\nOsseous structures are unremarkable.\nThere are no unexplained soft tissue calcifications or radiopaque foreign\nbodies.  Surgical clips in the right upper quadrant are compatible with prior\ncholecystectomy.\n\nIMPRESSION: \n\nConstipation without obstruction.\n","discharge_instructions":"You were admitted to the hospital due to nausea, vomiting, \nabdominal pain, and difficulty defecating. As you know, there \nremains some uncertainty regarding the cause of your symptoms. \nWe have not changed the current outpatient work-up plans, \nincluding colonoscopy, anorectal manometry, and gastric emptying \nstudy. While you were here we treated you with high doses of \nlaxatives for constipation. While this did cause diarrhea, it \nalso appears to have helped somewhat with you pain, which may \nargue that the constipation is playing a role in your abdominal \npain. We would recommend continuing to adjust your medications \nfor constipation as needed to acheieve ___ bowel movements per \nday with a soft/loose consistency. Senna and bisacodyl seemed to \nbe the medications that you tolerated best.\n\nGastroenterology has also recommended the following treatment \nfor your hemorrhoids and rectal fissure:\n\n 1. 2 tsp mineral oil daily or colace stool softner\n 2. 0.2 % nifedipine cream +  lidocaine 3%.  Needs to be made at \n___ or compounding pharmacy (___- \n___- ___ \n___, ___)\n 3. ___ baths in very warm water BID\n 4. +/- 1% topical hydrocortisone \n\nThey have also recommended the option of starting amitriptyline \nwith your psychiatrist, which is an antidepressant that can also \nhelp with abdominal pain.\n\nWe recommend minimizing tramadol as this can worsen \nconstiaption. Tylenol may also be effective for your pain. Avoid \nNSAIDs such as ibuprofen or naproxen.\n\nWe held your blood pressure medication, amlodipine, since it has \nthe potential to worsen constipation. Your blood pressures were \nin a good range while you were here. You should re-address this \nissue with your primary doctor.","brief_hospital_course":"___ year old woman with history of pancreatitis of unknown \netiology in ___, HTN, GERD, who presents with \nprogressive abdominal pain and difficulty with defecation. She \nhas been followed by gastroenterology in the outpatient setting \nand had multiple studies planned for work-up given the uncertain \ncause of her symptoms, including anorectal manometry, gastric \nemptying study, and colonoscopy. When evaluated by the \ngastroenterology team, it was noted that she had large external \nhemorrhoids and there was concern for fissure. Therefore it was \npostulated that painful defecation could have led to worsening \nconstipation, which could be driving much of her abdominal pain. \nWith this in mind, her bowel regimen was uptitrated \naggressively, which was successful in causing numerous large \nloose bowel movements. While the patient endorsed some \nimprovement in her abdominal pain, she also found it very \ndistressing to have that degree of diarrhea (of note she has \nexperienced considerable anxiety surrounding her symptoms and \nwas frequently tearful during the admission). During the \nadmission she was also offered topical treatments for rectal \npain, but declined them, as she did not feel that hemorrhoids or \nfissure were the cause of her symptoms. \n\nGiven the continued uncertainty surrounding her symptoms, she \nwill still plan for the outpatient diagnostic work-up as \ndetailed above. In the mean time she plans to titrate the bowel \nmedications to acheieve ___ loose/soft BMs daily. She was also \nprescribed topical treatments for her hemorrhoids and fissure, \nwhich she will consider. \n\nGI also recommended considering amitriptyline for functional \nabdominal pain, which she will discuss with her mental health \nprovider. \n\nNotably her amlodipine was held in case this was worsening her \nconstipation. Her BPs were wnl in house but if they are elevated \nin the future then another class of agent may be considered. \n\nPatient seen and examined on day of discharge. She was stable \nand safe to return home. She will arrange for PCP ___. \n\n======================================================".}
Your output should be in JSONL format. Write different discharge letter every time I run the code.
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
        max_tokens=3000,
        temperature=0.7,
        top_p=0.6,
        extra_headers={"X-Request-ID": f"discharge-{i:05}"},
        stream=False
    )

    chat_response = response.choices[0].message.content
    lines = chat_response.strip().split("\n")

    output_file_path = f"/home/IAIS/jdatta/mimic_syntheticData/english/synthetic_discharge_summaries_{i}.jsonl"

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
    # time.sleep(1)
