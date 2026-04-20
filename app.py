import streamlit as st
import re
from statistics import mean
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(
    page_title="Bundesliga RAG Explorer",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# Custom styling
# =========================
st.markdown("""
<style>
:root {
    --card: rgba(15, 23, 35, 0.82);
    --accent: #d00027;
    --accent-2: #ffd166;
    --muted: #b9c0cc;
    --border: rgba(255,255,255,0.10);
}

.stApp {
    background:
        linear-gradient(rgba(10, 14, 22, 0.94), rgba(10, 14, 22, 0.94)),
        radial-gradient(circle at top right, rgba(208,0,39,0.15), transparent 30%);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(16,23,34,0.95) 0%, rgba(13,19,29,0.98) 100%);
    border-right: 1px solid var(--border);
}

.hero {
    padding: 1.5rem 1.8rem;
    border-radius: 22px;
    background: linear-gradient(135deg, rgba(208,0,39,0.88), rgba(120,0,30,0.90));
    box-shadow: 0 18px 50px rgba(0,0,0,0.30);
    margin-bottom: 1rem;
}

.hero h1 {
    color: white;
    margin: 0;
    font-size: 2.3rem;
}

.hero p {
    color: rgba(255,255,255,0.92);
    margin-top: 0.6rem;
    font-size: 1.02rem;
}

.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 1.1rem 1.2rem;
    box-shadow: 0 12px 30px rgba(0,0,0,0.18);
}

.mini-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1rem;
    height: 100%;
}

.result-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 16px;
    padding: 1rem 1rem 0.7rem 1rem;
    margin-bottom: 0.8rem;
}

.badge {
    display: inline-block;
    padding: 0.3rem 0.65rem;
    border-radius: 999px;
    background: rgba(255,209,102,0.16);
    color: #ffe08a;
    font-size: 0.82rem;
    border: 1px solid rgba(255,209,102,0.25);
    margin-right: 0.45rem;
    margin-bottom: 0.35rem;
}

.small-muted {
    color: var(--muted);
    font-size: 0.95rem;
}

div[data-testid="metric-container"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid var(--border);
    padding: 0.8rem;
    border-radius: 16px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# DOCUMENTS
# =========================
DOCUMENTS = [
    """
    The Bundesliga, Germany's top professional football league, was founded in 1963 to modernize and centralize German football. Before that, football in West Germany was organized in regional leagues called Oberligen. The national champion was decided through a playoff system between regional winners. After Germany’s disappointing performance at the 1962 World Cup, football officials wanted a stronger national league that could improve competition and player development. The German Football Association approved the Bundesliga in 1962, and the first season began in 1963. 1. FC Köln became the first champion. Over time, the Bundesliga developed into one of Europe’s strongest football leagues, known for passionate fans, strong clubs, and historic rivalries.
    """,
    """
    The Bundesliga consists of 18 teams and follows a double round-robin format. Each team plays every other team twice, once at home and once away, resulting in 34 matches per season. A win gives 3 points, a draw 1, and a loss 0. The team with the most points at the end of the season wins the title. The bottom two teams are automatically relegated to the 2. Bundesliga, while the top two teams from the second division are promoted. The team finishing 16th plays a relegation playoff. This structure keeps both the title race and relegation battle exciting. The season usually runs from August to May and also includes domestic and European competitions.
    """,
    """
    Bayern Munich is the most successful club in Bundesliga history and has won more league titles than any other team. Borussia Dortmund is another major club, famous for its supporters, attacking football, and rivalry with Bayern. Other important Bundesliga clubs include Borussia Mönchengladbach, Werder Bremen, and VfB Stuttgart. In recent years, Bayer Leverkusen and RB Leipzig have also become major competitors. Bundesliga clubs are judged not only by titles, but also by European success, youth development, and stadium atmosphere. These clubs have shaped the identity and history of German football for decades.
    """,
    """
    The Bundesliga is famous for passionate derbies and rivalries. Der Klassiker between Bayern Munich and Borussia Dortmund is one of the most important fixtures each season. The Revierderby between Borussia Dortmund and Schalke 04 is one of Germany’s fiercest local rivalries. Other notable derbies include the Rhine Derby, Nordderby, and Berlin Derby. These matches are known for emotional intensity, historic significance, and extraordinary atmospheres in the stadiums. Rivalries are an essential part of Bundesliga culture and contribute to the league’s popularity both inside and outside Germany.
    """,
    """
    Bundesliga fan culture is widely considered one of the best in world football. German fans are known for standing terraces, choreographed tifos, and nonstop support during matches. Signal Iduna Park in Dortmund, with its famous Yellow Wall, is one of the most iconic stadiums in Europe. The Bundesliga is also known for relatively affordable ticket prices, which helps maintain strong connections between clubs and local communities. Matchday rituals, chants, scarves, and fan-led traditions create a unique atmosphere. This fan culture is one of the league’s defining strengths.
    """,
    """
    The Bundesliga's 50+1 rule requires clubs to retain majority fan ownership. At least 50 percent plus one voting share must remain with club members. This rule is designed to prevent full takeovers by outside investors and to preserve club identity. Supporters argue that it protects tradition, financial sustainability, and democratic involvement. Critics say it can limit clubs financially compared with leagues backed by billionaire or state ownership. Even so, 50+1 remains one of the defining features of German football and sets the Bundesliga apart from many other leagues.
    """,
    """
    Bundesliga legends include Gerd Müller, Franz Beckenbauer, Lothar Matthäus, and Robert Lewandowski. These players helped define German football through goals, leadership, and tactical influence. Gerd Müller became famous for his extraordinary finishing ability, while Beckenbauer transformed the role of the libero. Modern stars like Lewandowski and Manuel Neuer continued the Bundesliga’s tradition of excellence. Their success made the league globally respected and influenced football far beyond Germany.
    """,
    """
    The Bundesliga has strong international influence through European competitions, player development, coaching ideas, and global broadcasting. German clubs and coaches helped shape modern tactical football. Coaches like Jürgen Klopp and Thomas Tuchel spread Bundesliga ideas across Europe. The league is also respected for developing young players and combining financial sustainability with sporting success. This international reputation has strengthened the Bundesliga’s global profile.
    """,
    """
    Matchday atmosphere is a key reason why the Bundesliga is admired worldwide. Stadiums are often full, fans sing throughout the match, and choreographed tifos create unforgettable visual experiences. Clubs like Dortmund, Union Berlin, and St. Pauli are especially known for strong local identity. Supporters see football as part of community life, not just entertainment. That combination of passion, identity, and affordability makes Bundesliga culture unique.
    """,
    """
    Bayern Munich’s long dominance has shaped the Bundesliga era. Their success is based on strong finances, consistent management, elite players, and regular Champions League participation. However, competitors such as Borussia Dortmund and Bayer Leverkusen have challenged Bayern at different times. This tension between dominance and competition is a central theme in Bundesliga discussions. It also affects how fans think about fairness, rivalry, and excitement in the league.
    """
]

# =========================
# Chunking
# =========================
def chunk_text(text, chunk_size=180, overlap=40):
    words = text.split()
    chunks = []
    start = 0
    step = max(1, chunk_size - overlap)

    while start < len(words):
        chunk = " ".join(words[start:start + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
        start += step

    return chunks

def build_chunks(documents, chunk_size=180, overlap=40):
    all_chunks = []
    for doc in documents:
        all_chunks.extend(chunk_text(doc, chunk_size=chunk_size, overlap=overlap))
    return all_chunks

CHUNK_SIZE = 180
CHUNK_OVERLAP = 40
chunks = build_chunks(DOCUMENTS, CHUNK_SIZE, CHUNK_OVERLAP)

# =========================
# Search engine
# =========================
@st.cache_resource(show_spinner="Preparing search index...")
def build_search_index(_chunks):
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(_chunks)
    return vectorizer, matrix

vectorizer, doc_matrix = build_search_index(tuple(chunks))

def search_documents(query, top_k=4):
    query_vec = vectorizer.transform([query])
    scores = cosine_similarity(query_vec, doc_matrix)[0]
    ranked_indices = scores.argsort()[::-1][:top_k]
    results = [(chunks[i], float(scores[i])) for i in ranked_indices]
    return results

# =========================
# Sidebar
# =========================
st.sidebar.markdown("## ⚽ Bundesliga RAG")
st.sidebar.caption("Lightweight search through Bundesliga knowledge")
page = st.sidebar.radio("Navigate", ["Home", "Search", "Explore Chunks", "Statistics", "About"])
st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Topics")
st.sidebar.markdown("- History\n- Clubs\n- Derbies\n- Fans\n- 50+1 Rule")
st.sidebar.markdown("---")
st.sidebar.info(f"Search engine: TF-IDF\n\nChunking: {CHUNK_SIZE} / {CHUNK_OVERLAP}")

# =========================
# Home
# =========================
if page == "Home":
    st.markdown("""
    <div class="hero">
        <h1>⚽ Bundesliga RAG Explorer</h1>
        <p>Explore German football with lightweight semantic-style search. Discover clubs, rivalries, fan culture, and financial rules.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Documents", len(DOCUMENTS))
    c2.metric("Chunks", len(chunks))
    c3.metric("Search Type", "TF-IDF")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.4, 1])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("What this app does")
        st.write(
            "This Streamlit app searches Bundesliga texts using a lightweight retrieval approach. "
            "It ranks chunks by textual similarity and returns the most relevant passages for the user's question."
        )
        st.markdown("#### Try questions like:")
        st.markdown("- Which club has won the most Bundesliga titles?\n- What is the 50+1 rule?\n- Which derby is most famous?\n- What makes Bundesliga fan culture special?")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Knowledge areas")
        tags = ["History", "League Format", "Top Clubs", "Derbies", "Fan Culture", "50+1 Rule", "Players", "Europe"]
        st.markdown("".join([f'<span class="badge">{tag}</span>' for tag in tags]), unsafe_allow_html=True)
        st.markdown("<p class='small-muted'>Use the Search page to retrieve the most relevant chunks from these topics.</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# =========================
# Search
# =========================
elif page == "Search":
    st.markdown("""
    <div class="hero">
        <h1>🔎 Search</h1>
        <p>Ask a question about Bundesliga history, clubs, structure, rivalries, fan culture, or financial rules.</p>
    </div>
    """, unsafe_allow_html=True)

    sample_cols = st.columns(4)
    samples = [
        "Who has won the most Bundesliga titles?",
        "What is the 50+1 rule?",
        "Which derby is the most famous?",
        "Why is fan culture special?"
    ]
    for col, q in zip(sample_cols, samples):
        with col:
            st.caption("Example")
            st.code(q, language=None)

    query = st.text_input(
        "Search the knowledge base",
        placeholder="e.g. Why is Bundesliga fan culture considered special?",
    )
    num_results = st.slider("Number of results", 1, 6, 4)

    if query:
        with st.spinner("Searching relevant passages..."):
            results = search_documents(query, top_k=num_results)

        st.subheader(f"Top {len(results)} results")
        for i, (text, score) in enumerate(results, 1):
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown(f"**Result {i}**")
            st.progress(min(max(score, 0.0), 1.0))
            st.caption(f"Similarity score: {score:.3f}")
            st.write(text)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Enter a question above to search the Bundesliga knowledge base.")

    st.caption("Powered by TF-IDF vectorization and cosine similarity.")

# =========================
# Explore Chunks
# =========================
elif page == "Explore Chunks":
    st.markdown("""
    <div class="hero">
        <h1>🧩 Explore Chunks</h1>
        <p>Inspect how the documents are split into searchable pieces.</p>
    </div>
    """, unsafe_allow_html=True)

    lengths = [len(c) for c in chunks]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total chunks", len(chunks))
    m2.metric("Average size", f"{mean(lengths):.0f} chars")
    m3.metric("Smallest", f"{min(lengths)} chars")
    m4.metric("Largest", f"{max(lengths)} chars")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Why chunking matters")
    st.write(
        "Chunking affects retrieval quality. Smaller chunks can improve precision, while larger chunks preserve more context. "
        "This app uses chunking mainly to keep passages focused and easier to rank."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    for i, chunk in enumerate(chunks, 1):
        with st.expander(f"Chunk {i} — {len(chunk)} characters"):
            st.write(chunk)

# =========================
# Statistics
# =========================
elif page == "Statistics":
    st.markdown("""
    <div class="hero">
        <h1>📊 Statistics & Visualization</h1>
        <p>Explore document lengths, chunk counts, and compare chunking strategies.</p>
    </div>
    """, unsafe_allow_html=True)

    doc_lengths = [len(doc.strip()) for doc in DOCUMENTS]
    st.subheader("Document lengths")
    st.bar_chart({"Document Length": doc_lengths})

    chunk_counts = [len(chunk_text(doc, CHUNK_SIZE, CHUNK_OVERLAP)) for doc in DOCUMENTS]
    st.subheader("Chunks per document")
    st.bar_chart({"Chunks": chunk_counts})

    st.subheader("Chunking strategy comparison")
    comparison_data = {}
    for size in [100, 180, 260]:
        total_chunks = sum(len(chunk_text(doc, size, 40)) for doc in DOCUMENTS)
        comparison_data[f"chunk_size={size}"] = total_chunks

    st.bar_chart(comparison_data)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Why this matters")
    st.write(
        "Smaller chunk sizes create more chunks and can improve retrieval precision, while larger chunk sizes preserve more context. "
        "This page helps explain the trade-off behind the chosen chunking strategy."
    )
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# About
# =========================
elif page == "About":
    st.markdown("""
    <div class="hero">
        <h1>ℹ️ About This Project</h1>
        <p>A lightweight Bundesliga search app built for a Retrieval-Augmented Generation homework assignment using Streamlit and scikit-learn.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="mini-card">', unsafe_allow_html=True)
        st.subheader("Tech stack")
        st.markdown("- Streamlit\n- scikit-learn\n- TF-IDF\n- Cosine Similarity")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="mini-card">', unsafe_allow_html=True)
        st.subheader("Project focus")
        st.markdown("- Bundesliga history\n- Clubs and records\n- Rivalries\n- Fan culture\n- Financial rules")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.success("This app demonstrates a lightweight document retrieval system for Bundesliga knowledge.")