import jieba
stopwords = [line.strip() for line in open('../../stopwords.txt', encoding='gb18030').readlines()]
print(stopwords)
def seg_depart(sentence):
     print("正在分词")
     sentence_depart = jieba.cut(sentence.strip())
     outstr = ''
     for word in sentence_depart:
         if word not in stopwords:
             if word != '\t':
                 outstr += word
                 outstr += " "
     return outstr
print(seg_depart("日本富士电视台下午远程连线采访了我，向我了解一下"))