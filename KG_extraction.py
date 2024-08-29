import csv

def load_sentence_data(_sentence_file_path : str):
    with open(_sentence_file_path,encoding='utf-8', newline='') as csvfile:
        rows = csv.DictReader(csvfile)
        sentence_list = []
        for row in rows:
            sentence_list.append(row)
    return sentence_list
if __name__ == '__main__':
    input_file = "test_input_data.csv"
    KG_file = "test_data.csv"
    outputn_file = "KG_extraction.csv"
    input_sentences = load_sentence_data(input_file)
    KG_sentences = load_sentence_data(KG_file)

    extraction = [['head','relation','tail']]

    for word in input_sentences:
        if word['relation'] == None or word['tail'] == None:
            continue
        for KG_sentence in KG_sentences:
            if (word['head'] == KG_sentence['head'] or word['relation'] == KG_sentence['relation'] or word['tail'] == KG_sentence['tail']) \
                and [KG_sentence['head'],KG_sentence['relation'],KG_sentence['tail']] not in extraction:
                extraction.append([KG_sentence['head'],KG_sentence['relation'],KG_sentence['tail']])
    print(extraction,end='\n')


    
    with open(outputn_file, 'w', newline='', encoding='utf-8') as csvfile:
        try:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerows(extraction)
        except:
            print('csv encoding error')