import streamlit as st
import numpy as np
import base64
import os
from statistics import mean

st.set_page_config(
    page_title="Bundesliga RAG Explorer",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# =========================
# Custom styling
# =========================


bg_image = get_base64_image("visuals/dortmund-stadium-view-scaled.jpg")

st.markdown(f"""
<style>
:root {{
    --bg: #0e1117;
    --card: linear-gradient(135deg, rgba(26,32,44,0.95), rgba(17,24,39,0.92));
    --accent: #d00027;
    --accent-2: #ffd166;
    --text: #f5f7fb;
    --muted: #b9c0cc;
    --border: rgba(255,255,255,0.10);
}}

.stApp {{
    background: transparent;
}}

.stApp::before {{
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image:
        linear-gradient(rgba(10, 14, 22, 0.85), rgba(10, 14, 22, 0.85)),
        url("data:image/jpeg;base64,{bg_image}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
    z-index: -2;
}}

.stApp::after {{
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at top right, rgba(208,0,39,0.18), transparent 25%);
    z-index: -1;
}}


.block-container {{
    padding-top: 2rem;
    padding-bottom: 2rem;
}}

section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, rgba(16,23,34,0.92) 0%, rgba(13,19,29,0.95) 100%);
    border-right: 1px solid var(--border);
}}

.hero {{
    padding: 1.6rem 1.8rem;
    border-radius: 22px;
    background: linear-gradient(135deg, rgba(208,0,39,0.88), rgba(120,0,30,0.90));
    box-shadow: 0 18px 50px rgba(0,0,0,0.30);
    margin-bottom: 1rem;
}}

.hero h1 {{
    color: white;
    margin: 0;
    font-size: 2.5rem;
}}

.hero p {{
    color: rgba(255,255,255,0.92);
    margin-top: 0.6rem;
    font-size: 1.05rem; 
}}

.card {{
    background: rgba(15, 23, 35, 0.78);
    backdrop-filter: blur(8px);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 1.1rem 1.2rem;
    box-shadow: 0 12px 30px rgba(0,0,0,0.18);
}}

.mini-card {{
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(8px);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1rem;
    height: 100%;
}}

.result-card {{
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(6px);
    border: 1px solid rgba(255,255,255,0.09);
    border-left: 5px solid var(--accent);
    border-radius: 16px;
    padding: 1rem 1rem 0.7rem 1rem;
    margin-bottom: 0.8rem;
}}

.badge {{
    display: inline-block;
    padding: 0.3rem 0.65rem;
    border-radius: 999px;
    background: rgba(255,209,102,0.16);
    color: #ffe08a;
    font-size: 0.82rem;
    border: 1px solid rgba(255,209,102,0.25);
    margin-right: 0.45rem;
    margin-bottom: 0.35rem;
}}

.small-muted {{
    color: var(--muted);
    font-size: 0.95rem;
}}

div[data-testid="metric-container"] {{
    background: rgba(255,255,255,0.04);
    border: 1px solid var(--border);
    padding: 0.8rem;
    border-radius: 16px;
}}

.stTextInput > div > div > input {{
    border-radius: 14px;
}}
</style>
""", unsafe_allow_html=True)

# =========================
# DOCUMENTS
# =========================
DOCUMENTS = [
      # 1. History and Founding of the Bundesliga (~350 words)
    """
    The Bundesliga, Germany's top professional football league, was founded in 1963 to modernize and centralize German football. Prior to its creation, football in West Germany was organized in regional leagues called Oberligen. The national champion was then decided through a playoff system between regional winners. After Germany’s disappointing performance at the 1962 World Cup, football officials wanted a stronger national league that could improve the level of competition and help German clubs and players develop more consistently.
    On July 28, 1962, the German Football Association voted in favor of creating the Bundesliga. The league began with 16 founding clubs, selected according to sporting success, economic stability, and regional balance. The first Bundesliga season started in August 1963, and 1. FC Köln became the first champion. Over time, the league expanded, introduced promotion and relegation changes, and developed into one of the strongest football leagues in Europe.
    Today, the Bundesliga is known for its history, strong fan culture, and competitive football. It has played an important role in the development of German football and has helped shape many world-class players and successful clubs.
    """,

    # 2. League Structure and Format (~350 words)
    """
    The Bundesliga consists of 18 teams that compete against each other in a double round-robin format. This means every club plays each other twice during the season: once at home and once away. As a result, each team plays 34 matches in total. A win gives a team 3 points, a draw gives 1 point, and a loss gives 0 points. At the end of the season, the club with the most points wins the Bundesliga title.
    The bottom two teams are automatically relegated to the 2. Bundesliga, while the top two teams from the 2. Bundesliga are promoted. In addition, the team finishing 16th in the Bundesliga plays a relegation playoff against the team finishing 3rd in the second division. This system makes the league exciting not only at the top of the table, but also at the bottom.
    The Bundesliga season usually runs from August to May and includes a winter break. Clubs also compete in domestic and European competitions such as the DFB-Pokal, UEFA Champions League, and UEFA Europa League.
    """,

    # 3. Top Clubs and Achievements (~350 words)
    """
    Bayern Munich is the most successful club in Bundesliga history and has won more league titles than any other team. The club has dominated German football for long periods, especially in the modern era. Borussia Dortmund is another major Bundesliga club, known for its passionate supporters, attacking football, and strong rivalry with Bayern Munich. Other important clubs include Borussia Mönchengladbach, Werder Bremen, and VfB Stuttgart.
    These clubs have shaped the history of the league through championships, memorable matches, and famous players. In recent years, Bayer Leverkusen and RB Leipzig have also become important competitors in the Bundesliga. Leverkusen, in particular, has grown into a serious title contender and has challenged Bayern’s dominance.
    The success of Bundesliga clubs is not only measured by league titles, but also by their performances in European competitions, their stadium atmosphere, and their ability to develop talented players.
    """,

    # 4. Famous Rivalries and Derbies (~350 words)
    """
    The Bundesliga is home to some of the world's most passionate derbies. Der Klassiker between Bayern Munich and Borussia Dortmund is one of the most anticipated matches each season. This rivalry is not about geography but pure competition for the championship title. Bayern leads with 55 wins in 111 meetings, while Dortmund has 26 victories. The first Klassiker was in 1965, with Dortmund winning 2-0. Robert Lewandowski added intensity by scoring 23 goals against his former club Dortmund while playing for Bayern.
    The Revierderby between Borussia Dortmund and Schalke 04 is known as the 'mother of all derbies.' These clubs from Germany's Ruhr industrial region have working-class fan bases and fierce local pride. Dortmund leads 37-32 in 100 Bundesliga meetings. A famous match was in 2017 when Dortmund led 4-0 at halftime but Schalke equalized 4-4. The clubs are just 20.5 miles apart, making it a true neighborhood battle.
    The Original Klassiker pits Bayern Munich against Borussia Mönchengladbach. These teams dominated German football in the 1970s with stars like Gerd Müller and Günter Netzer. Bayern leads 54-28 in 113 matches. Gladbach won three straight titles from 1974-77 but Bayern has since dominated.
    Other notable derbies include the Rhine Derby (Cologne vs. Mönchengladbach), Nordderby (Hamburg vs. Werder Bremen), and Berlin Derby (Hertha vs. Union Berlin). Each has unique history and passionate supporters. The Hamburg Derby between HSV and St. Pauli represents class differences, while the Baden-Swabia Derby between Stuttgart and Karlsruhe dates back to regional political rivalries.
    These derbies create intense atmospheres and memorable moments that define Bundesliga culture.
    """,

    # 5. Record Champions and Stats (~300 words)
    """
    Bayern Munich holds the record with 33 Bundesliga titles since 1963, more than half of all championships. They achieved an unprecedented 11 consecutive titles from 2013 to 2023, the longest streak in any major European league. Bayern also won the 2024/25 title, extending their dominance.
    Borussia Dortmund has 5 titles, including back-to-back wins in 1995/96 and 2011/12. Borussia Mönchengladbach also has 5 championships, winning three straight from 1975-77. Werder Bremen and Hamburger SV each have 4 titles, while VfB Stuttgart has 3.
    Thirteen different clubs have won the Bundesliga in 61 seasons. Bayer Leverkusen ended Bayern's streak by winning their first title in 2023/24. 1. FC Köln won the inaugural 1963/64 championship.
    Individual records include Gerd Müller's 365 goals for Bayern. Bayern set the points record with 91 in 2012/13. Manuel Neuer holds records for most clean sheets (212) and wins (311).
    Financially, champions earn €65-70 million from domestic prize money plus Champions League revenue. 87% of recent champions reached the Champions League Round of 16.
    The league's competitive balance is maintained through financial regulations and revenue sharing. Bayern's dominance has sparked discussions about competitive parity.
    """,

    # 7. Current Season Highlights 2025/26 (~280 words)
    """
    The 2025/26 Bundesliga season features familiar faces and new challenges. Bayern Munich started strongly, defeating RB Leipzig 6-0 in their opener. Harry Kane continues his prolific scoring, leading Bayern's title defense.
    Bayer Leverkusen, fresh off their 2023/24 breakthrough, aims to defend their recent success. Xabi Alonso's tactical innovations make them dangerous. Borussia Dortmund seeks to challenge Bayern in Der Klassiker matches.
    RB Leipzig and VfB Stuttgart represent the new challengers. Leipzig's high-pressing style creates exciting matches. Union Berlin's defensive organization keeps them competitive.
    Key fixtures include Bayern vs. Dortmund (October 18, 2025, Bayern won 2-1), Gladbach vs. Bayern (October 25, Bayern 3-0), and the Rhine Derby (Gladbach 3-1 Cologne). Attendance remains high, averaging over 38,000 per match.
    Standings show Bayern leading, followed closely by Leverkusen and Dortmund. Relegation battle involves traditional clubs fighting for survival. Young talents like Florian Wirtz (Leverkusen) and Jamal Musiala (Bayern) shine.
    European implications are significant, with top four spots determining Champions League qualification. The season promises drama with title race, derbies, and promotion battles.
    """,

    # 8. Fan Culture and Atmosphere (~310 words)
    """
    Bundesliga matches feature some of the world's best atmospheres. German fans are renowned for standing terraces, choreographed tifos, and passionate support throughout 90 minutes. The league averages over 38,000 spectators per match, second only to the English Premier League.
    Signal Iduna Park (Dortmund) holds the record with 81,365 capacity. The Yellow Wall is football's largest standing terrace, creating an intimidating atmosphere for visiting teams. Borussia Dortmund fans sing "You'll Never Walk Alone" and coordinate massive displays.
    Bayern Munich's Allianz Arena (75,000) features red LED lighting that changes color during matches. The Südkurve ultras group creates elaborate choreographies. Schalke 04's Veltins Arena (62,000) has a retractable roof and pitch, with passionate Ruhr area support.
    St. Pauli's Millerntor-Stadion represents counterculture with left-wing politics and punk aesthetics. HSV fans maintain the North Stand tradition despite relegation. Union Berlin's Alte Försterei (22,000) punches above its size with intense support.
    German football culture emphasizes community ownership through the 50+1 rule. Fans influence club decisions and maintain affordable tickets (€15-25 average). Pyrotechnics, though officially banned, remain part of the culture.
    Matchday rituals include pre-game marches, scarves held aloft, and coordinated chants. The atmosphere contributes to the league's global appeal, with TV deals reaching 200+ countries.
    """,

    # 9. Financial Rules like 50+1 (~290 words)
    """
    The Bundesliga's 50+1 rule requires clubs to maintain majority fan ownership, distinguishing it from other leagues. At least 50% plus one share of voting rights must belong to club members. This prevents billionaire takeovers and ensures fan influence.
    The rule promotes financial stability and prevents debt spirals seen elsewhere. Clubs cannot spend more than they earn through the licensing system. Revenue sharing distributes TV money equally (50%) rather than performance-based like Premier League.
    Average Bundesliga ticket prices are €25, compared to €60+ in England. This accessibility builds strong fan bases and stadium atmospheres. Commercial revenue comes from sponsorships, merchandise, and international TV deals (€1.1 billion annually).
    Bayern Munich generates €800 million revenue through global brand, stadium, and Champions League. RB Leipzig challenges 50+1 through Red Bull sponsorship structure. Hertha BSC faced issues after investor Klaus-Michael Kühne acquired 66% shares.
    The DFL (German Football League) enforces squad cost rules limiting spending to 85% of revenue by 2025/26. This contrasts with state-owned clubs like PSG and Manchester City.
    50+1 preserves club identity and prevents financial doping. Critics argue it limits competitiveness against oil-funded rivals, but supporters value democratic structure. The model has influenced discussions in other leagues.
    """  
]

# =========================
# Cache heavy resources
# =========================
@st.cache_resource(show_spinner="Loading embedding model...")
def load_embedding_model():
    from langchain_huggingface import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )

@st.cache_resource(show_spinner="Building vector database...")
def build_vector_store(_documents: tuple):
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import Chroma

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=180,
        chunk_overlap=40,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = []
    for doc in _documents:
        chunks.extend(splitter.split_text(doc.strip()))

    embeddings = load_embedding_model()

    vector_store = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        collection_name="bundesliga_knowledge_base",
    )

    return vector_store, chunks

vector_store, chunks = build_vector_store(tuple(DOCUMENTS))

# =========================
# Sidebar
# =========================
st.sidebar.markdown("## ⚽ Bundesliga RAG")
st.sidebar.caption("Semantic search through Bundesliga knowledge")
page = st.sidebar.radio("Navigate", ["Home", "Search", "Explore Chunks", "Statistics", "About"])
st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Topics")
st.sidebar.markdown("- History\n- Clubs\n- Derbies\n- Fans\n- 50+1 Rule")
st.sidebar.markdown("---")
st.sidebar.info("Model: all-MiniLM-L6-v2\n\nChunking: 120 / 20")

# =========================
# Home
# =========================
if page == "Home":
    st.markdown("""
    <div class="hero">
        <h1>⚽ Bundesliga RAG Explorer</h1>
        <p>Explore German football with semantic search. Search by meaning, discover clubs, rivalries, fan culture, and financial rules.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Documents", len(DOCUMENTS))
    c2.metric("Topic Areas", len(DOCUMENTS))
    c3.metric("Embedding Model", "MiniLM")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.4, 1])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("What this app does")
        st.write(
            "This Streamlit app uses embeddings and a Chroma vector database to search Bundesliga texts semantically. "
            "Instead of matching only keywords, it finds passages that are similar in meaning to your query."
        )
        st.markdown("#### Try questions like:")
        st.markdown("- Which club has won the most Bundesliga titles?\n- What is the 50+1 rule?\n- Which derby is most famous?\n- How does relegation work?\n- What makes Bundesliga fan culture special?")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Knowledge areas")
        tags = ["History", "League Format", "Top Clubs", "Derbies", "Fan Culture", "50+1 Rule"]
        st.markdown("".join([f'<span class="badge">{tag}</span>' for tag in tags]), unsafe_allow_html=True)
        st.markdown("<p class='small-muted'>Use the Search page to retrieve the most relevant chunks from these topics.</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# =========================
# Search
# =========================
elif page == "Search":
    st.markdown("""
    <div class="hero">
        <h1>🔎 Semantic Search</h1>
        <p>Ask a question about Bundesliga history, clubs, structure, rivalries, fan culture, or financial rules.</p>
    </div>
    """, unsafe_allow_html=True)

    sample_cols = st.columns(4)
    samples = [
        "Who has won the most Bundesliga titles?",
        "What is the 50+1 rule?",
        "Which derby is the most famous?",
        "How does relegation work?"
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
        with st.spinner("Searching semantic matches..."):
            results = vector_store.similarity_search_with_score(query, k=num_results)

        st.subheader(f"Top {len(results)} results")
        for i, (doc, score) in enumerate(results, 1):
            similarity = max(0.0, 1 - float(score))
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown(f"**Result {i}**")
            st.progress(min(similarity, 1.0))
            st.caption(f"Estimated relevance: {similarity:.2f}")
            st.write(doc.page_content)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Enter a question above to search the Bundesliga knowledge base.")

    st.caption("Powered by all-MiniLM-L6-v2 embeddings and ChromaDB.")

# =========================
# Explore Chunks
# =========================
elif page == "Explore Chunks":
    st.markdown("""
    <div class="hero">
        <h1>🧩 Explore Chunks</h1>
        <p>Inspect how the text splitter breaks the documents into searchable semantic pieces.</p>
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
        "Chunking affects retrieval quality. Smaller chunks can be more precise, while larger chunks preserve more context. "
        "This app uses chunk_size=180 and chunk_overlap=40 to keep memory usage low on deployment while still preserving useful context."
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
        <p>Explore document lengths, chunk counts, and the structure of the knowledge base.</p>
    </div>
    """, unsafe_allow_html=True)

    from langchain_text_splitters import RecursiveCharacterTextSplitter

    doc_lengths = [len(doc.strip()) for doc in DOCUMENTS]

    st.subheader("Document lengths")
    st.bar_chart({"Document Length": doc_lengths})

    splitter_current = RecursiveCharacterTextSplitter(
        chunk_size=180,
        chunk_overlap=40,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunk_counts = [len(splitter_current.split_text(doc.strip())) for doc in DOCUMENTS]

    st.subheader("Chunks per document")
    st.bar_chart({"Chunks": chunk_counts})

    st.subheader("Chunking strategy comparison")
    chunk_sizes = [100, 120, 180]
    comparison_data = {}

    for size in chunk_sizes:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=size,
            chunk_overlap=20,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        total_chunks = sum(len(splitter.split_text(doc.strip())) for doc in DOCUMENTS)
        comparison_data[f"chunk_size={size}"] = total_chunks

    st.bar_chart(comparison_data)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Why this matters")
    st.write(
        "Smaller chunk sizes create more chunks and can improve precision, while larger chunk sizes preserve more context. "
        "This comparison shows why choosing the right chunk size matters in a semantic search application."
    )
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# About
# =========================
elif page == "About":
    st.markdown("""
    <div class="hero">
        <h1>ℹ️ About This Project</h1>
        <p>A semantic search app built for a Retrieval-Augmented Generation homework assignment using Streamlit, LangChain, ChromaDB, and sentence-transformer embeddings.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="mini-card">', unsafe_allow_html=True)
        st.subheader("Tech stack")
        st.markdown("- Streamlit\n- LangChain\n- ChromaDB\n- sentence-transformers\n- all-MiniLM-L6-v2")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="mini-card">', unsafe_allow_html=True)
        st.subheader("Project focus")
        st.markdown("- Bundesliga history\n- Clubs and records\n- Rivalries\n- Fan culture\n- Financial rules")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.success("This app demonstrates how semantic search can turn a small document collection into a searchable knowledge base.")