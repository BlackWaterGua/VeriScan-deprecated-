from fastapi import FastAPI
import torch
import modelUse
from QueryGeneration.QueryGenerator import QueryGenerator
import re
from SentenceBert.SentenceBert import get_similar_sentence
from Prompt.P_tuning_v1 import P_tuning_v1

# uvicorn main:app --host 0.0.0.0 --port 80
app = FastAPI()

# {'SUPPORTS': 0, 'REFUTES': 1, 'NOT ENOUGH INFO': 2}
unique_tags = ['SUPPORTS', 'REFUTES', 'NOT ENOUGH INFO']
tag2id = {tag: id for id, tag in enumerate(unique_tags)}
id2tag = {id: tag for tag, id in tag2id.items()}

tokenizer, model = modelUse.model_init()

@app.get("/")
async def predict(claim: str, evidence:str):
    inputs = tokenizer(text=claim, text_pair=evidence, padding=True, truncation=True, max_length=128, return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits
    result_id = logits.argmax().item()
    result = id2tag[result_id]
    return {"model": "bert-large-cased", "result": result}

@app.get("/equery/")
async def api_001(claim: str):
    try:
        queryGenerator = QueryGenerator("t5", "t5-base")
        queryGenerator.training_args.batch_size = 8
        queryGenerator.training_args.max_seq_length = 64
        queryGenerator.training_args.decoder_max_length = 20
        queryGenerator.model.load_state_dict(torch.load('./FactVerificaionAPI/ckeckpoint/queryGenerator.pth'))
        query = queryGenerator.predict([claim])
        return {"equery":query[0], "state":"1"}

    except Exception as e:
        return {"equery":None, "state":e}

@app.get("/everify/")
async def api_002(claim: str, url:str):
    try:
        text = url_to_text(url)
        evidences = re.split(r'(?<=[.?!;])\s+', text)
        evidences = list(evidence for evidence in evidences if len(evidence) > 50)
        gold_evidences = get_similar_sentence(claim, evidences, 'bert-base-uncased', f"./FactVerificaionAPI/checkpoint/sentenceBert_bert_checkpoint.ckpt", )
        
        verifi_model = P_tuning_v1("bert","bert-base-uncased")
        verifi_model.model.load_state_dict(torch.load("./FactVerificaionAPI/checkpoint/p_tuning_bert.pth"))
        most_label, most_evidences = verifi_model.predict(claim, gold_evidences)
        return {"label":most_label, "evidence":most_evidences, "state":"1"}

    except Exception as e:
        return {"label":None, "evidence":None, "state":e}

@app.get("/cverify/")
async def api_003(claim: str, url:str):
    try:
        text = url_to_text(url)
        evidences = re.split(r'[？：。！（）.“”…\t\n]', text)
        evidences = [evidence for evidence in evidences if len(evidence) > 5]
        gold_evidences = get_similar_sentence(claim, evidences, './FactVerificaionAPI/ckeckpoint/roberta_pretrain', f"./FactVerificaionAPI/checkpoint/sentenceBert_bert_chinese.ckpt", )
        

        return {"label":None, "evidence":None, "state":"1"}

    except Exception as e:
        return {"label":None, "evidence":None, "state":e}
