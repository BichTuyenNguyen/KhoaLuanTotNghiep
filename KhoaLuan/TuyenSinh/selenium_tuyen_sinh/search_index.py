"""
    Đánh chỉ mục cho tài liệu và search theo query
"""
from whoosh.index import create_in
from whoosh import index
from whoosh.fields import *
from whoosh.qparser import QueryParser
from pymongo import MongoClient
import underthesea as uts
import re
import nltk
from nltk.tokenize import RegexpTokenizer
import os, os.path

def word_separation(s):
    """
    Tách từ trong câu
    :return: List
    """
    text = uts.word_sent(s, format='text')# tách từ
    tokenizer = RegexpTokenizer('\w+')# lấy từ và trả về một mảng danh sách các từ đã tách
    tokens = tokenizer.tokenize(text)
    return tokens   # ['đăng_kí', 'nguyện_vọng', '1', 'như', 'thế_nào', 'Em', 'cảm_ơn', 'ạ']

def clearn_stop_word(tokens):
    stop_words_tuyensinh = [u'dạ',u'mình', u'tôi', u'cho', u'em', u'hỏi', u'ạ', u'tôi', u'cảm_ơn', u'cám_ơn', u'chị', u'anh',u'chị',
                            u'thầy_cô', u'thầy', u'cô', u'vâng', u'vậy', u'e_e', u'c', u'ii',u'bị', u'bởi', u'cả',u'là',
                            u'các', u'cái', u'cần', u'càng', u'chỉ', u'chiếc', u'cho', u'chứ', u'chưa', u'chuyện', u'có',
                            u'có_thể', u'cứ', u'của', u'cùng', u'cũng', u'đã', u'đang', u'đây', u'để', u'đến_nỗi', u'đều',
                            u'điều', u'do', u'đó', u'được', u'dưới', u'gì', u'khi', u'không', u'lại', u'lên', u'lúc', u'mà',
                            u'mỗi', u'một_cách', u'này', u'nên', u'nếu', u'ngay', u'nhiều', u'như', u'nhưng', u'những', u'nơi',
                            u'nữa', u'phải', u'qua', u'ra', u'rằng', u'rất', u'rồi', u'sau', u'sẽ', u'so', u'sự', u'tại', u'theo',
                            u'thì', u'trên', u'trước', u'từ', u'từng', u'và', u'vẫn', u'vào', u'vậy', u'vì', u'việc', u'với', u'vừa']

    stop_words = nltk.corpus.stopwords.words('english') # lấy các stop word của tiếng anh đã được download cmd: nltk.download('stopwords')
    word_clear = stop_words + stop_words_tuyensinh# tạo ra một list bao gồm stop word của tiếng anh và một số từ tiếng việt cần loại bỏ khỏi câu hỏi
    result = ''
    for word in tokens:
        word = word.lower()
        if word not in word_clear:
            result += word + ' '
    result = result.strip()
    return result
# Cho em hỏi là điểm thi đại học của em dưới điểm sàn thì có được nộp nguyện vọng 2 vào các trường cao đẳng không ?
def indexing():
    """
    Đánh chỉ mục và search dựa vào câu query
    :param s:  câu truy vấn đã làm sạch : #dạ cho em hỏi, em muốn đăng ký nguyện vọng 1 thì như thế nào ạ?
    :return: list các tài liệu được tìm thấy
    """
    client = MongoClient('mongodb://localhost:27017/') #kết nối MongoDB
    db = client.DBTuyenSinh #ket noi database
    collection = db.WordSegmentation  #ket noi collection của Database
    select_table = collection.find({}, {"_id":0})#read data
    # tiến hành đánh chỉ mục
    schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT)
    if not os.path.exists("Data_index"):
        os.mkdir("Data_index")
    ix = create_in("Data_index", schema)
    writer = ix.writer()
    for item in select_table:
        content = item['questions'] + ' ' + item['answers'] + ' ' + item['dates']
        writer.add_document(title=content, path=u"/a", content='')
    writer.commit()

def search_documents(s):
    # tiến hành search dựa vào câu truy vấn và parse title
    results_search = []
    results_search.append(s)
    ix = index.open_dir("Data_index")
    with ix.searcher() as searcher:
        query = QueryParser("title", ix.schema).parse(s)
        results = searcher.search(query)
        if len(results) <= 0:
            return 0
        else:
            for hit in results:
                results_search.append(hit['title'])
            return results_search

def search_index_main():
    question_input = input('Nhập câu hỏi của bạn: ')
    question_input = re.sub(r"(\s{2,})", '', question_input)
    tokens = word_separation(question_input)
    s = clearn_stop_word(tokens)
    # indexing()
    results_search_main = search_documents(s)
    return results_search_main

if __name__ == '__main__':
    kq = search_index_main()
    if kq == 0:
        print("Không có kết quả phù hợp với câu hỏi!")
    else:
        print('Số lượng document sau khi tìm kiếm là: %d' %(len(kq)-1))
        for j in range(len(kq)):
            if j == 0:
                print('Tiền xử lý câu truy vấn: ', kq[j])
            else:
                print(kq[j])

# Cho em hỏi . em thi rớt đại học , em sẽ có 3 giấy báo điểm , em sử dụng 3 giấy báo điểm ấy đăng ký nguyện vọng 2 vào 3 trường khác nhau được không ạ
#Quy chế tuyển sinh 2017 vừa được Bộ Giáo dục Đào tạo ban hành có những điểm gì mới so với năm trước ?