from django.shortcuts import render
import pandas as pd

from django.http import  JsonResponse
from django.views.decorators.csrf import csrf_exempt

# ne names
ne_name =['EVENT','FAC','GPE','LANGUAGE','LAW','LOC','NORP','ORG','PERSON','PRODUCT','WORK_OF_ART']
idx2nename = { str(i) : item for i, item in enumerate(ne_name)}

# category names
news_categories=['心情','閒聊','美食','時事']
idx2cate = { str(i) : item for i, item in enumerate(news_categories)}

def load_data_topNer():
    # read data
    df_data= pd.read_csv('app_top_ner/dataset/dcardall_by_ner_and_category.csv')

    global data
    data = {}
    for idx, (nerName, topKeys) in df_data.iterrows():
        data[nerName] = dict(eval(topKeys))

# We should call load_data() at first.
load_data_topNer()

def home(request):
    return render(request,'app_top_ner/home.html')

# When Post is used, the csrf of this function should be ignored
@csrf_exempt
def api_get_ner_topword(request):
    # POST方式取得新聞類別
    cate = request.POST.get('news_category')
    cate = idx2cate[cate]

    # 取得多少筆關鍵詞
    topk = int(request.POST.get('topk'))

    ner_value = request.POST.get('ner_value')
    ner_value = idx2nename[ner_value]

    print(ner_value, cate, topk)

    responseData = get_category_topkey(ner_value, cate, topk)
    response = {'data': responseData }
    print(response)
    return JsonResponse(response)


def get_category_topkey(ner_value, cate, topk):

    wf_pairs = data[ner_value][cate][0:topk]

    if wf_pairs == []:
        return []

    words = [w for w, f in wf_pairs]
    freqs = [f for w, f in wf_pairs]

    # Prepare cloud chart data
    # the minimum and maximum frequency of top words
    min_ = wf_pairs[-1][1]  # the last line is smaller
    max_ = wf_pairs[0][1]   # the first frequency value is larger

    textSizeMin = 30
    textSizeMax = 180

    if (min_ != max_):
        max_min_range = max_ - min_

    else:
        max_min_range = len(wf_pairs)
        min_ = min_ - 1

    # cloud chart data
    # using proportional scaling
    clouddata = [{'text':w, 'size':int(textSizeMin+(f - min_)/max_min_range*(textSizeMax-textSizeMin))} for w, f in wf_pairs]

    responseData = {
        "wf_pairs": wf_pairs,
        "data_barchart":{
                        "category": cate,
                        "labels": words,
                        "values": freqs
                        },
        "data_cloud": clouddata}
    return responseData


print("app_top_ner載入成功!")
