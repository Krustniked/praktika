from flask import Blueprint, jsonify, request
from . import db
from sqlalchemy import select
from models import Answer, Token
import string, re, nltk
from nltk.corpus import stopwords
from pymystem3 import Mystem


main = Blueprint("main", __name__)
nltk.download('stopwords')
nltk.download('wordnet')





def get_tokens(text):
    text = text.lower().translate(str.maketrans(string.punctuation,' '*len(string.punctuation)))
    text = re.sub(r'\s+', ' ', str(text)).strip()
    stop_words = stopwords.words('russian')
    stop_words.extend(['…', '«', '»', '...', ' ', '\n'])
    text = Mystem().lemmatize(text)
    text = [token for token in text if token not in stop_words]
    return text

@main.route("/api/GetStatus")
def index():
    return jsonify({"status": "ок"})

@main.route("/api/AddAnswer")
def add_answer():
    answe = request.args.get("answer")
    if not answe:
        if request.is_json:
            data = request.get_json()
            answe = data.get('answer')

    if answe:
        # Выполняем SQL-запрос для проверки существования ответа
        checking_response = db.session.execute(select(Answer).where(Answer.text == answe)).scalars().first()       
        if checking_response:                                                                              
            
            return jsonify(status="error", description="This answer already exists.")                        
                                                                     
        db.session.add(Answer(text = answe))                                                            
        db.session.commit()
        return jsonify(status = "ok")
    else:
        return jsonify(status="error", description="The answer cannot be empty.")
    
@main.route("/api/GetAnswers")
def get_answers():
    answers = db.session.execute(select(Answer)).scalars().all()
    if answers:
        return jsonify(answers = [answer.to_dict() for answer in answers])
    else:
        return jsonify(answers = None)

@main.route("/api/GetAnswerById", methods=['POST', 'GET'])
def get_id():
        answer_id = request.args.get("id")        
        answer = db.session.execute(select(Answer).filter_by(id = answer_id)).scalars().first()
        if answer:
            return jsonify(answer = answer.text)
        else:
            return jsonify(answers = None)
        
        
@main.route("/api/AskQuestion", methods = ['POST', 'GET'])
def ask_question():
    question = request.get_json().get("question") if request.is_json else request.args.get("question") 
    if question:
        question_tokens = get_tokens(question)
        unique_tokens = set(question_tokens)
        fanswers = {}
        for token in unique_tokens:
            answers = db.session.execute(select(Answer).where(Answer.tokens.any(Token.text == token))).scalars().all()
            if answers and len(answers) > 0:
                for answer in answers:
                    if answer.id in fanswers:
                        fanswers[answer.id] += 1
                    else:
                        fanswers[answer.id] = 1
                        
        if fanswers:
            result = dict(sorted(fanswers.items(), key=lambda item: item[1], reverse=True))
            answer_id = list(result.keys())[0]
            fanswer = db.session.get(Answer, answer_id)
            return jsonify(answer = fanswer.text)
        
        return jsonify(asked_question = question )
    else:
        return jsonify(status = "error", description = "no question")
    
    
@main.route("/api/AddTokensForAnswer")
def add_tokens():
    answer_id = request.get_json().get("id") if request.is_json else request.args.get("id")
    tokens = request.get_json().get("tokens") if request.is_json else request.args.get("tokens")
    
    if not answer_id or not tokens:
        return jsonify(status = "error", description = "no answer id or tokens")
    
    try:
        answer = db.session.get(Answer, int(answer_id))
    except:
        return jsonify(status = "error", description = "id must be numeric")
    
    if not answer:
        return jsonify(status = "error", description = "answer not found")
    
    avilable_tokens = []
    if isinstance(tokens, list):
        for token in tokens:
            avilable_tokens.extend(get_tokens(token))
    elif isinstance(tokens, str):
        avilable_tokens.extend(get_tokens(tokens))
    else: 
        return jsonify(status = "error", description = "tokens must be list or str")
    
    if len(avilable_tokens) == 0:
        return jsonify(status = "error", description = "no tokens")
    
    avilable_tokens = list(set(avilable_tokens)) #set для того, чтобы исключить повторяющиеся токены
    for token in avilable_tokens:
        exist_token = db.session.execute(select(Token).where(Token.text == token)).scalars().first()
        if exist_token:
            if sum(answ.id == answer.id for answ in exist_token.answers) == 0:
                answer.tokens.append(exist_token)
        else:
            new_token = Token(text = token)
            new_token.answers.append(answer)
            db.session.add(new_token)
    db.session.commit()
    return jsonify(status = "ok")