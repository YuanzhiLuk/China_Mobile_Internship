import csv
import requests
import json
import ast

# ===== var setting  =====

input_file_path = './sentence_entities.json'
output_relation_file_path = './test_data.csv'

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
            "system": '你是帮忙判断提取SPO三元组的好帮手',
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

def GPT_relation_extraction(_sentence : str, _entity_list : list , _filter: bool = True) -> list:
    prompt_1 = "\n 请从以下文本中提取主语-谓语-宾语三元组（SPO三元组），并只用以[[主语，谓语，宾语]，…]的形式回答，注意答案中的主语必须包含主语列表提供的实体，否则直接去除： "  +  \
    "\n例如:" + \
    "\n給定句子 : 美国参议院针对今天总统布什所提名的劳工部长赵小兰展开认可听证会，预料她将会很顺利通过参议院支持，成为该国有史以来第一位的华裔女性内阁成员。" + \
    "\n主语和宾语列表：[ '布什'，'赵小兰'，'参议院']" + \
    "\nSPO三元组：[['布什'，'提名'，'赵小兰']，['参议院'，'展开认可听证会'，'赵小兰']]" + \
    "\n主语和宾语列表：" + str(_entity_list) +\
    "\n给定句子 : " + _sentence + \
    "\nSPO三元组 : "     

    prompt_2 = "\n请从以下文本中提取主语-谓语-宾语三元组（SPO三元组），并以[[主语，谓语，宾语]，…]的形式回答，注意答案中的主语必须包含主语列表提供的实体，否则直接去除："  +  \
    "\n例如:" + \
    "\n给定句子：641年3月2日文成公主入藏，与松赞乾布和亲。" + \
    "\n主语和宾语列表：['松赞干布'，'文成公主']" + \
    "\nSPO三元組 : [['松赞干布' , '妻子' , '文成公主' ],['文成公主' , '丈夫' , '松赞干布' ]]" + \
    "\n主语和宾语列表：" + str(_entity_list) +\
    "\n给定句子 : " + _sentence + \
    "\nSPO三元组 : "     


    # prompt setting 
    prompt = prompt_1 

    # MODEL_TYPE ='gpt-3.5-turbo' 


    start_idx = 0
    result = []
    print("\n ============================")
    print("\n主语和宾语列表：" + str(_entity_list))
    print("\n给定句子：" + _sentence)

    while start_idx < len(prompt):
        end_idx = min(start_idx + 1600, len(prompt))

        response = GetBaiduAi(
            question=prompt,
            model_url=modelUrl,
            APIKey=apiKey,
            SecretKey=secretKey
        )
        print(response.split(":")[-1])
        response = response.split(":")[-1]
        if response.strip() == "":
            continue
        str_res = ""
        for letter in range(len(response)):
            if response[letter] == '[':
                while letter < len(response) and response[letter] != ']':
                    str_res += response[letter]
                    letter += 1
                str_res += "]"
        if len(str_res)<=2:
            continue
        if str_res[0]=="[" and str_res[1]!="[":
            str_res = "["+str_res
        if str_res[-1]=="]" and str_res[-2]!="]":
            str_res = str_res+"]"
        for letter in range(len(str_res)-1):
            if str_res[letter]=="]" and str_res[letter+1]=="[":
                str_res = str_res[:letter+1]+","+str_res[letter+1:]
            elif str_res[letter]=="[" and str_res[letter+1]=="[" and letter!=0:
                str_res = str_res[:letter+1]+str_res[letter+2:]
            elif str_res[letter]=="]" and str_res[letter+1]=="]" and letter!=len(str_res)-1:
                str_res = str_res[:letter+1]+str_res[letter+2:]

        print(str_res)

        print("\n GPT : " + str_res)
        try:
            GPT_result = ast.literal_eval(str_res)  # change GPT massage string as list
            for item in GPT_result:
                print(item)
                # TODO : filter condition change to search whole entity list
                if(not _filter):
                    result.append(item)
                elif((item[0] in _entity_list) and (item[2] in _entity_list) ):  # only head and tail object both in NER will be filtered out
                    result.append(item)
        except:
            print ("GPT exception")
            continue

        start_idx = end_idx
    return result
# ========  main   ========


sentence_list = []
with open(input_file_path, 'r' , encoding='utf8') as jsonfile:
    data = json.load(jsonfile)


# extract relation & save result into csv file


relation_list = [['head', 'relation', 'tail']]

for data_ele  in data :
    # if no entity be reconized , skip extraction
    if(not(data_ele['entity'])):
        continue

    relation_result = (GPT_relation_extraction(data_ele['sentence'], data_ele['entity'],False))
    for relation_ele in relation_result:
        relation_list.append(relation_ele)


# 開啟CSV檔案並將內容清空
with open(output_relation_file_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow([])  # 寫入空白的一列，即清空CSV檔案內容


with open(output_relation_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    print(relation_list)
    try:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(relation_list)
    except:
        print('csv encoding error')




