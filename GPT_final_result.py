import csv
import requests
import json

# ===== var setting  =====

output_relation_file_path = './result_data.csv'

# GPT_key_file_path = './GPT_key.txt'
apiKey  = ''
secretKey = ''
modelUrl = 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/yi_34b_chat'

# ====== def function  ======
def GetAccessToken(APIKey, SecretKey):
    """
    使用 API Key，Secret Key 获取access_token，替换下列示例中的应用API Key、应用Secret Key
    网址：https://console.bce.baidu.com/qianfan/ais/console/applicationConsole/application
    """

    url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={}&client_secret={}".format(
        APIKey, SecretKey)

    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")
def GetBaiduAi(question, model_url, APIKey, SecretKey):
    try:
        url = "{}?access_token=".format(model_url) + GetAccessToken(APIKey, SecretKey)
 
        payload = json.dumps({
            "temperature": 0.95,
            "top_p": 0.7,
            "system": '你是帮忙判断信息并给出答案的好帮手',
            "messages": [
                {
                    "role": "user",
                    "content": question
                }
            ]
        })
        headers = {
            'Content-Type': 'application/json'
        }
 
        response = requests.request("POST", url, headers=headers, data=payload)
 
        content = response.text
        content = json.loads(content)
        resultContent = content["result"]
        return resultContent
    except Exception as e:
        print(e)
        return str(e)

def load_sentence_data(_sentence_file_path : str):
    with open(_sentence_file_path,encoding='utf-8', newline='') as csvfile:
        rows = csv.DictReader(csvfile)
        sentence_list = []
        for row in rows:
            sentence_list.append(row)
    return sentence_list

def GPT_get_result() -> list:
    input_file = "KG_extraction.csv"
    input_sentences = load_sentence_data(input_file)
    _sentence = ""
    que_file = "input_sentences.csv"
    que_sentences = load_sentence_data(que_file)
    _ques = ""
    for word in que_sentences:
        _ques += word['Sentence']
    for word in input_sentences:
        if word['head'] == None or word['relation'] == None or word['tail'] == None:
            continue
        _sentence += "["+word['head']+word['relation']+word['tail']+"],"
    prompt_1 = "请根据以下相关信息的SPO三元组，给出所求问题的答案：\
        其中SPO三元组为："+(_sentence)+"。其中，问题为:"+_ques

    response = GetBaiduAi(
        question=prompt_1,
        model_url=modelUrl,
        APIKey=apiKey,
        SecretKey=secretKey
    )

    return response
# ========  main   ========

result = (GPT_get_result())



with open(output_relation_file_path, 'w', newline='', encoding='utf-8') as file:
    print(result)
    try:
        file.write(result)
    except:
        print('write error')




