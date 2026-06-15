import re
import pandas as pd
import nltk
from nltk.corpus import stopwords

# Download corpora sekali (idempotent — aman dipanggil berkali-kali)
try:
    stopwords.words('indonesian')
except LookupError:
    nltk.download('stopwords', quiet=True)

# Slang dictionary
_SLANG_URL = 'https://raw.githubusercontent.com/nasalsabila/kamus-alay/master/colloquial-indonesian-lexicon.csv'
try:
    _slang_df = pd.read_csv(_SLANG_URL)
    slang_map = dict(zip(_slang_df['slang'], _slang_df['formal']))
except Exception:
    slang_map = {}  # fallback jika offline

# Pre-compile regex
RE_MENTION = re.compile(r'@[A-Za-z0-9]+')
RE_HASHTAG = re.compile(r'#[A-Za-z0-9]+')
RE_RT = re.compile(r'RT[\s]')
RE_URL = re.compile(r'http\S+')
RE_NUMBERS = re.compile(r'[0-9]+')
RE_NON_ALPHANUM = re.compile(r'[^\w\s]')

# Stopwords (negasi DIPERTAHANKAN)
negations = {'tidak', 'bukan', 'tiada', 'tak', 'jangan', 'tanpa', 'kurang'}
stop_words = set(stopwords.words('indonesian')) - negations
stop_words.update(['yg', 'dg', 'rt', 'nya', 'sih', 'ke', 'di', 'dari', 'tersebut', 'ini', 'itu'])

def preprocess_text(text):
    text = RE_MENTION.sub('', text)
    text = RE_HASHTAG.sub('', text)
    text = RE_RT.sub('', text)
    text = RE_URL.sub('', text)
    text = RE_NUMBERS.sub('', text)
    text = RE_NON_ALPHANUM.sub(' ', text)
    text = text.lower().strip()
    tokens = text.split()
    tokens = [slang_map.get(w, w) for w in tokens]
    tokens = [w for w in tokens if w not in stop_words]
    return ' '.join(tokens)