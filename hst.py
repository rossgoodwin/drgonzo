from pattern.en import parsetree, parse
from pattern.vector import stem, PORTER, LEMMA
from nltk.corpus import wordnet as wn
import string
import random
from pymongo import MongoClient
from time import sleep
# import en

def make_lookup():
    tags = []

    for doc in tagColl.find():
        for c in doc["concepts"]:
            tags.append(c["text"])
            
    tags = [t.lower() for t in list(set(tags))]

    lookup = {}

    for t in tags:
        lookup[t.lower()] = []

    for t in tags:
        lookup[stem(t.lower(), stemmer=PORTER)] = []
        
    for doc in tagColl.find():
        for c in doc["concepts"]:
            lookup[c["text"].lower()].append([doc["_id"], c["relevance"]])
            lookup[stem(c["text"].lower(), stemmer=PORTER)].append([doc["_id"], c["relevance"]])
            
    for k in lookup.keys():
        lookup[k] = sorted(lookup[k], key=lambda x: x[1])
        lookup[k] = [x[0] for x in lookup[k]]

    return lookup


def synonymous(word):
    synonyms = []
    ss = wn.synsets(word.lower())
    for s in ss:
        synonyms+=s.lemma_names()

    for i in range(len(synonyms)):
        synonyms[i] = string.replace(synonyms[i], '_', ' ')
        
    synonyms = set(synonyms)
    return synonyms


def extract_overlap(blah, lookup):
    # Parse input text...

    s = parsetree(blah, relations=True, lemmata=True)

    keywords = []
    raw = []
    adj = []
    all_tokens = []

    for sentence in s:
        for chunk in sentence.subjects + sentence.objects:
            h = chunk.head
            if h.type != "PRP":
                keywords.append(h.string)
                raw.append(chunk.string)
        for word in sentence.words:
            if word.type == "JJ":
                adj.append(word.string)
            all_tokens.append(word.string)

    # Make candidate lists...

    key_cand = []
    syn_key_cand = []
    stem_key_cand = []

    adj_cand = []
    syn_adj_cand = []
    stem_adj_cand = []

    all_cand = []
    syn_all_cand = []
    stem_all_cand = []

    last_resort = []

    tags = [k.lower() for k in lookup.keys()]
    
    for word in keywords:
        if word.lower() in tags:
            key_cand.append(word.lower())
        for synword in synonymous(word):
            if synword.lower() in tags:
                syn_key_cand.append(synword.lower())
        if stem(word.lower(), stemmer=PORTER) in tags:
            stem_key_cand.append(stem(word.lower(), stemmer=PORTER))


    for word in adj:
        if word.lower() in tags:
            adj_cand.append(word.lower())
        for synword in synonymous(word):
            if synword.lower() in tags:
                syn_adj_cand.append(synword.lower())
        if stem(word.lower(), stemmer=PORTER) in tags:
            stem_adj_cand.append(stem(word.lower(), stemmer=PORTER))
            
    for word in all_tokens:
        if word.lower() in tags:
            all_cand.append(word.lower())
        for synword in synonymous(word):
            if synword.lower() in tags:
                syn_all_cand.append(synword.lower())
        if stem(word.lower(), stemmer=PORTER) in tags:
            stem_all_cand.append(stem(word.lower(), stemmer=PORTER))
                
    for k in tags:
        if k.lower() in blah.lower():
            last_resort.append(k)

    cand = key_cand + stem_key_cand + adj_cand + stem_adj_cand + all_cand + stem_all_cand + syn_key_cand + syn_adj_cand + syn_all_cand + last_resort

    if cand == None:
        cand = []

    return cand


def getfiletext(fn):
    f = open('ghost/'+fn+'.txt')
    t = f.read()
    f.close()
    return t

def intro():
    print "\n\n\n\n\n\nYOU ARE WAITING IN A WAITING ROOM."

    for _ in range(5):
        sleep(1)
        print "\nWAITING..."

    sleep(1)
    print "\nDR. GONZO WILL SEE YOU NOW."

    sleep(2)
    print "\nStep into my office."

    sleep(3)
    print "\nQuickly! Shut the goddamn door you lurid golem!\n"
    x = raw_input("> ")

    return x


def zero(r):
    sleep(1)
    r = r.lower()

    question = ['?', 'who', 'what', 'when', 'where', 'why', 'how']
    exclaim = ['wow', 'woah']
    office = ['office', 'room',]
    door = ['door', 'shut', 'close']
    words = ['golem', 'lurid', 'insult', 'mean', 'word', 'language']
    sorry = ['sorry', 'apologize', 'apologies']

    if any(q in r for q in question):
        print "\n" + getfiletext('question') + "\n"
        x = raw_input("> ")
        general(x)

    elif any(e in r for e in exclaim):
        print "\n" + getfiletext('exclaim') + "\n"
        x = raw_input("> ")
        general(x)

    elif any(o in r for o in office):
        print "\n" + getfiletext('office') + "\n"
        x = raw_input("> ")
        general(x)

    elif any(d in r for d in door):
        print "\n" + getfiletext('door') + "\n"
        x = raw_input("> ")
        general(x)

    elif any(w in r for w in words):
        print "\n" + getfiletext('words') + "\n"
        # x = raw_input("> ")
        general("", words=True) # TODO FIX THIS

    elif any(s in r for s in sorry):
        print "\n" + getfiletext('sorry') + "\n"
        x = raw_input("> ")
        general(x)

    else:
        general("")


def general(r, words=False):
    if not words:
        print "\n" + getfiletext('general') + "\n"
    x = raw_input("> ")
    lu = make_lookup()
    y = computation(extract_overlap(x, lu) + extract_overlap(r, lu), lu)
    z = football(y, lu)
    while True:
        z = computation(z, lu)


def football(rl, lookup):
    print "\n" + getfiletext('football') + "\n"
    x = raw_input("> ")
    print "\n" + getfiletext('suicide') + "\n"
    y = raw_input("> ")
    xl = extract_overlap(x, lookup)
    yl = extract_overlap(y, lookup)
    return yl + xl + rl


def computation(rl, lookup):
    global used_ids
    obj_list = []
    tag_list = []
    rl.reverse() # IMPORTANT
    for tag in rl:
        for obj in lookup[tag]:
            if not obj in used_ids:
                tag_list.append(tag)
                obj_list.append(obj)
    if obj_list:
        # print obj_list
        doc = tagColl.find_one({"_id": obj_list[-1]})
        print "\n" + doc["text"] + " " + append_custom(tag_list[-1]) + "\n"
        used_ids.append(obj_list[-1])
    else:
        print "\n" + "I have nothing for you." + "\n"
    x = raw_input("> ")
    rl.reverse() # IMPORTANT
    return extract_overlap(x, lookup) + rl


def append_custom(word):
    raw = getfiletext('append_dyno')
    dyno = raw.split('\n')
    raw = getfiletext('append_static')
    static = raw.split('\n')

    appender = random.choice(dyno+static)
    appender = string.replace(appender, '[x]', word)

    return appender




client = MongoClient()

db = client.hst_db
tagColl = db.tagged
untagColl = db.untagged

used_ids = []

zero(intro())


