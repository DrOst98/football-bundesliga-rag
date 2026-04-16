"""
RAG Knowledge Base - Starter Template
FAMNIT AI Course - Day 3

A simple Retrieval-Augmented Generation (RAG) app built with
Streamlit, LangChain, and ChromaDB. No API keys needed!

Instructions:
    1. Replace the DOCUMENTS list below with your own texts
    2. Update the app title and description
    3. Run locally:  streamlit run app.py
    4. Deploy to Render (see assignment instructions)
"""

import streamlit as st
import numpy as np

st.set_page_config(
    page_title="My RAG Knowledge Base",
    page_icon="🔍",
    layout="wide",
)

# ──────────────────────────────────────────────────────────────────────
# YOUR DOCUMENTS — Replace these with your own topic!
# Each string is one "document" that will be chunked, embedded, and
# stored in the vector database for semantic search.
# ──────────────────────────────────────────────────────────────────────
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

    # 6. Iconic Players and Legacies (~320 words)
    """
    The Bundesliga has produced legendary players who shaped football history. Gerd Müller, nicknamed 'Der Bomber,' scored 365 goals in 427 games for Bayern Munich, winning 4 titles and 3 European Cups. Franz Beckenbauer revolutionized the libero position, leading Bayern to 4 titles and earning the nickname 'Der Kaiser.'
    Günter Netzer was Mönchengladbach's creative genius during their 1970s golden era. Lothar Matthäus captained Germany to the 1990 World Cup and won 7 Bundesliga titles with Bayern.
    Modern icons include Robert Lewandowski, who scored 344 goals for Dortmund and Bayern, winning 11 titles. Manuel Neuer redefined goalkeeping with his sweeper-keeper style, winning 12 titles.
    Michael Ballack led Leverkusen to the 2002 treble attempt and won titles with Bayern. Bastian Schweinsteiger was Bayern's midfield engine for a decade. Mats Hummels anchored Dortmund's defenses during their title wins.
    Klinsmann, Rummenigge, and Breitner from the 1980s represented German football excellence. Current stars like Harry Kane continue the tradition at Bayern.
    These players not only won trophies but changed how football is played. Beckenbauer invented the modern defender role, Müller redefined finishing, Neuer transformed goalkeeping. Their legacies extend beyond statistics to tactical innovation and cultural impact.
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
    """,

    # 10. International Impact and European Successes (~300 words)
    """
    The Bundesliga has won more UEFA Champions League titles (8) than any other league. Bayern Munich's 2020 final victory over PSG was their sixth. Dortmund won in 1997 against Juventus. Hamburg (1983) and Frankfurt (2022 Conference League) add to the tally.
    German clubs reached 13 Champions League finals since 1997. Bayern's 2013 final featured three Bundesliga teams (Bayern, Dortmund, Leverkusen). The league's high-pressing, counter-attacking style translates well to Europe.
    Bundesliga exports 500+ players annually, including Haaland, Bellingham, Musiala. The league serves as a development ground for talents before Premier League moves. Revenue from transfers (€1 billion+ annually) funds youth academies.
    Global TV deals reach 200 countries, generating €1.1 billion. International fan bases grow through digital platforms and tours. The league's reputation for exciting football attracts viewers.
    German clubs dominate European coefficients, securing extra Champions League spots. Financial model produces sustainable success rather than boom-bust cycles.
    Success stories include Leverkusen's 2024 Europa League win and Frankfurt's 2022 Conference League triumph. Dortmund's 1997 Champions League victory remains a high point for non-Bayern clubs.
    The Bundesliga's international impact extends to coaching. Klopp, Tuchel, Nagelsmann influence global tactics. The league balances domestic success with European competitiveness.
    """      
]

# ──────────────────────────────────────────────────────────────────────
# Cached heavy resources (loaded once, reused across reruns)
# ──────────────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner="Loading embedding model...")
def load_embedding_model():
    from langchain_huggingface import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


@st.cache_resource(show_spinner="Building vector database...")
def build_vector_store(_documents: tuple):
    """Chunk documents, embed them, and store in ChromaDB."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import Chroma

    # --- Chunking ---
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = []
    for doc in _documents:
        chunks.extend(splitter.split_text(doc))

    embeddings = load_embedding_model()

    # --- Store in ChromaDB ---
    vector_store = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        collection_name="knowledge_base",
    )
    return vector_store, chunks

# ──────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────
st.sidebar.title("My RAG App")
page = st.sidebar.radio("Navigate", ["Home", "Search", "Explore Chunks"])

# ──────────────────────────────────────────────────────────────────────
# HOME PAGE
# ──────────────────────────────────────────────────────────────────────
if page == "Home":
    st.title("My RAG Knowledge Base")
    st.markdown("""
    Welcome! This app lets you **search documents by meaning**, not just keywords.

    ### How it works
    1. **Documents** are split into small chunks
    2. Each chunk is converted to an **embedding** (a vector of numbers)
    3. Chunks are stored in a **vector database** (ChromaDB)
    4. When you search, your query is embedded and compared to all chunks
    5. The most **semantically similar** chunks are returned

    ### Get started
    - Go to **Search** to ask questions
    - Go to **Explore Chunks** to see how documents are split

    ---
    *Built with Streamlit, LangChain, and ChromaDB*
    """)

    st.info(f"Knowledge base contains **{len(DOCUMENTS)} documents**.")


# ──────────────────────────────────────────────────────────────────────
# SEARCH PAGE
# ──────────────────────────────────────────────────────────────────────
elif page == "Search":
    st.title("Semantic Search")
    st.markdown("Ask a question and the app will find the most relevant chunks from the knowledge base.")

    vector_store, chunks = build_vector_store(tuple(DOCUMENTS))

    query = st.text_input(
        "Your question",
        placeholder="e.g. What is RAG?",
    )
    num_results = st.slider("Number of results", 1, 10, 3)

    if query:
        with st.spinner("Searching..."):
            results = vector_store.similarity_search_with_score(query, k=num_results)

        st.subheader(f"Top {len(results)} results")
        for i, (doc, score) in enumerate(results, 1):
            # ChromaDB returns distance; lower = more similar
            similarity = max(0, 1 - score)  # rough conversion
            with st.container():
                st.markdown(f"**Result {i}** — relevance: `{similarity:.2f}`")
                st.markdown(f"> {doc.page_content}")
                st.divider()

    st.markdown("---")
    st.caption("Powered by all-MiniLM-L6-v2 embeddings + ChromaDB")

# ──────────────────────────────────────────────────────────────────────
# EXPLORE CHUNKS PAGE
# ──────────────────────────────────────────────────────────────────────
elif page == "Explore Chunks":
    st.title("Explore Chunks")
    st.markdown("See how your documents are split into chunks by the recursive text splitter.")

    vector_store, chunks = build_vector_store(tuple(DOCUMENTS))
    st.metric("Total chunks", len(chunks))

    lengths = [len(c) for c in chunks]
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg chunk size", f"{np.mean(lengths):.0f} chars")
    col2.metric("Min chunk size", f"{min(lengths)} chars")
    col3.metric("Max chunk size", f"{max(lengths)} chars")

    st.subheader("All chunks")
    for i, chunk in enumerate(chunks, 1):
        with st.expander(f"Chunk {i} ({len(chunk)} chars)"):
            st.text(chunk)

