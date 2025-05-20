import streamlit as st
import pandas as pd
import plotly.express as px
import snowflake.connector
from PIL import Image

# Set up page configuration
st.set_page_config(
    page_title="India's Cultural Heritage Explorer",
    page_icon="🪔",
    layout="wide"
)

# Connect to Snowflake (placeholder - credentials would be in secrets)
@st.cache_resource
def init_connection():
    return snowflake.connector.connect(
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        account=st.secrets["snowflake"]["account"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"]
    )

conn = init_connection()

# App header
st.title("🎨 India's Living Cultural Heritage")
st.subheader("Explore Traditional Art Forms & Promote Responsible Cultural Tourism")

# Navigation
tab1, tab2, tab3, tab4 = st.tabs([
    "Art Forms Gallery", 
    "Cultural Destinations", 
    "Tourism Insights", 
    "Responsible Tourism"
])

with tab1:
    st.header("Traditional Art Forms of India")
    
    # Fetch art forms data from Snowflake
    @st.cache_data
    def get_art_forms():
        return pd.read_sql("SELECT * FROM art_forms", conn)
    
    art_forms = get_art_forms()
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        selected_state = st.selectbox("Filter by State", ["All"] + sorted(art_forms['state'].unique()))
        selected_category = st.selectbox("Filter by Category", ["All"] + sorted(art_forms['category'].unique()))
        
        if selected_state != "All":
            art_forms = art_forms[art_forms['state'] == selected_state]
        if selected_category != "All":
            art_forms = art_forms[art_forms['category'] == selected_category]
    
    with col2:
        for _, row in art_forms.iterrows():
            with st.expander(f"{row['art_form']} - {row['state']}"):
                col_img, col_desc = st.columns([1, 2])
                with col_img:
                    try:
                        st.image(Image.open(f"images/{row['image_path']}"), width=200)
                    except:
                        st.image(Image.open("images/default_art.jpg"), width=200)
                with col_desc:
                    st.markdown(f"""
                    **Origin**: {row['origin']}  
                    **Materials**: {row['materials']}  
                    **Description**: {row['description']}  
                    **Cultural Significance**: {row['significance']}  
                    """)
                    if row['video_url']:
                        st.video(row['video_url'])

with tab2:
    st.header("Cultural Destinations Across India")
    
    # Fetch destinations data
    @st.cache_data
    def get_destinations():
        return pd.read_sql("SELECT * FROM cultural_destinations", conn)
    
    destinations = get_destinations()
    
    # Map visualization
    st.subheader("Interactive Map of Cultural Hotspots")
    fig = px.scatter_mapbox(
        destinations,
        lat="latitude",
        lon="longitude",
        hover_name="name",
        hover_data=["state", "category", "annual_visitors"],
        color="category",
        zoom=4,
        height=600,
        mapbox_style="carto-positron"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Hidden gems section
    st.subheader("Hidden Gems - Lesser Known Cultural Sites")
    hidden_gems = destinations[destinations['annual_visitors'] < 10000].sort_values('significance', ascending=False)
    for _, row in hidden_gems.head(5).iterrows():
        st.markdown(f"""
        ### {row['name']}, {row['state']}
        **Category**: {row['category']}  
        **Significance**: {row['significance']}  
        **Why visit?**: {row['unique_aspect']}  
        **Best time to visit**: {row['best_season']}  
        """)
        st.image(Image.open(f"images/{row['image_path']}"), width=500)

with tab3:
    st.header("Tourism Trends and Insights")
    
    # Fetch tourism data
    @st.cache_data
    def get_tourism_data():
        return pd.read_sql("SELECT * FROM tourism_trends", conn)
    
    tourism_data = get_tourism_data()
    
    # Seasonality analysis
    st.subheader("Seasonality of Cultural Tourism")
    selected_site = st.selectbox("Select a cultural site", tourism_data['site_name'].unique())
    site_data = tourism_data[tourism_data['site_name'] == selected_site]
    
    fig = px.line(
        site_data,
        x="month",
        y="visitor_count",
        title=f"Monthly Visitors to {selected_site}",
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Government initiatives
    st.subheader("Government Initiatives for Cultural Preservation")
    initiatives = pd.read_sql("SELECT * FROM government_initiatives", conn)
    for _, row in initiatives.iterrows():
        st.markdown(f"""
        ### {row['initiative_name']}
        **Ministry**: {row['ministry']}  
        **Year launched**: {row['year_launched']}  
        **Budget allocated**: ₹{row['budget']:,}  
        **Impact**: {row['impact_description']}  
        """)

with tab4:
    st.header("Responsible Cultural Tourism")
    
    st.markdown("""
    ## How to Be a Responsible Cultural Tourist
    
    ### Do's
    - Respect local customs and traditions
    - Purchase authentic handicrafts directly from artisans
    - Follow photography guidelines at sacred sites
    - Dress appropriately for cultural sites
    - Learn basic local phrases
    
    ### Don'ts
    - Don't touch artifacts or artworks without permission
    - Avoid bargaining aggressively with local artisans
    - Don't participate in exploitative cultural performances
    - Avoid littering at heritage sites
    
    ## Supporting Artisan Communities
    """)
    
    # Artisan support programs
    programs = pd.read_sql("SELECT * FROM artisan_programs", conn)
    for _, row in programs.iterrows():
        st.markdown(f"""
        ### {row['program_name']}
        **Organization**: {row['organization']}  
        **Art forms supported**: {row['art_forms_supported']}  
        **How to participate**: {row['participation_details']}  
        [Learn more]({row['website_url']})
        """)

# Footer
st.markdown("---")
st.markdown("""
**Data Sources**: [Data.gov.in](https://www.data.gov.in), Ministry of Tourism, Archaeological Survey of India  
**Note**: This application is for educational purposes to showcase India's cultural heritage.
""")
