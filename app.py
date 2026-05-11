import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuration & Styling ---
st.set_page_config(page_title="Global Job Market Dashboard", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS to match a Premium Modern Dark Theme
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Hide top header bar and reduce app padding */
    header {visibility: hidden;}
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        max-width: 95% !important;
    }
    
    /* Style for metric containers (KPI Cards) */
    div[data-testid="metric-container"] {
        background-color: #243447;
        border: 1px solid #334155;
        padding: 5px 15px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    /* Metric Value text */
    div[data-testid="stMetricValue"] {
        color: #e0f2fe;
        font-size: 2rem;
        font-weight: 800;
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.2);
    }
    /* Metric Label text */
    div[data-testid="stMetricLabel"] {
        color: #94a3b8;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Dropdown / Multiselect styling */
    div[data-baseweb="select"] > div {
        border-radius: 8px !important;
        border: 1px solid #334155 !important;
        background-color: #1e293b !important;
        transition: all 0.2s ease;
        max-height: 46px !important;
        overflow-y: auto !important;
    }
    div[data-baseweb="select"] > div:focus-within {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 8px rgba(56, 189, 248, 0.3) !important;
    }
    
    /* Title styling */
    .main-title {
        text-align: center;
        color: #38bdf8;
        font-size: 32px;
        font-weight: 800;
        margin-top: -20px;
        margin-bottom: 10px;
        letter-spacing: -0.5px;
    }
</style>
""", unsafe_allow_html=True)


# --- Load Data ---
# --- Data Loading & Feature Engineering (Combined) ---
@st.cache_data
def load_data():
    # Load the dataset using the correct reader for the file type.
    data_path = 'data/data_jobs_salary_clean.xlsx'
    if data_path.lower().endswith(('.xls', '.xlsx')):
        df = pd.read_excel(data_path)
    else:
        df = pd.read_csv(data_path)
    
    # 2. Parse dates and create the 'Posted Date' column for your line chart
    df['job_posted_date'] = pd.to_datetime(df['job_posted_date'], errors='coerce')
    df['Posted_Month'] = df['job_posted_date'].dt.strftime('%Y-%m')

    # 3. Create Experience Category (Logic from add_features.py)
    def determine_experience(title):
        if pd.isna(title): return 'Mid'
        title_lower = str(title).lower()
        import re
        if re.search(r'\b(senior|sr\.?|lead|principal|staff|director|manager|head|chief|vp|president)\b', title_lower):
            return 'Senior'
        if re.search(r'\b(junior|jr\.?|entry|intern|associate|graduate|trainee|student)\b', title_lower):
            return 'Entry'
        return 'Mid'
    
    df['experience_category'] = df['job_title'].apply(determine_experience)

    # 4. Create Salary Range Category (Logic from add_features.py)
    q33 = df['salary_year_avg'].quantile(0.33)
    q67 = df['salary_year_avg'].quantile(0.67)
    
    def determine_salary_range(salary):
        if pd.isna(salary): return 'Unknown'
        elif salary <= q33: return 'Low'
        elif salary <= q67: return 'Medium'
        else: return 'High'
            
    df['salary_category'] = df['salary_year_avg'].apply(determine_salary_range)
    
    return df

# Initialize the integrated dataframe
df = load_data()

# --- Dashboard Header & Title ---
st.markdown('<div class="main-title">Global Job Market & Salary Dashboard</div>', unsafe_allow_html=True)


# --- Layout Top Row: KPIs and Filters ---
top_col1, top_col2 = st.columns([3, 2])

with top_col2:
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        experience_levels = st.multiselect("Experience", options=df["experience_category"].dropna().unique(), default=[])
    with f_col2:
        locations = st.multiselect("Location", options=df["job_country"].dropna().unique(), default=[])
    with f_col3:
        job_titles = st.multiselect("Job Title", options=df["job_title_short"].dropna().unique(), default=[])

# Apply Filters
df_filtered = df.copy()
if experience_levels:
    df_filtered = df_filtered[df_filtered["experience_category"].isin(experience_levels)]
if locations:
    df_filtered = df_filtered[df_filtered["job_country"].isin(locations)]
if job_titles:
    df_filtered = df_filtered[df_filtered["job_title_short"].isin(job_titles)]

# Calculate KPIs
total_jobs = len(df_filtered)
avg_salary = df_filtered["salary_year_avg"].mean()
max_salary = df_filtered["salary_year_avg"].max()
remote_jobs = len(df_filtered[df_filtered["job_work_from_home"] == 1])

with top_col1:
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Total Jobs", f"{total_jobs:,}")
    with k2:
        val = f"${avg_salary:,.0f}" if pd.notna(avg_salary) else "N/A"
        st.metric("Average Salary", val)
    with k3:
        val = f"${max_salary:,.0f}" if pd.notna(max_salary) else "N/A"
        st.metric("Maximum Salary", val)
    with k4:
        st.metric("Remote Roles", f"{remote_jobs:,}")

# --- Common Chart Theme Settings ---
chart_layout = dict(
    paper_bgcolor='#1e293b',
    plot_bgcolor='#1e293b',
    font=dict(color='#94a3b8'),
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(gridcolor='rgba(255,255,255,0.05)', zerolinecolor='rgba(255,255,255,0.05)'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.05)', zerolinecolor='rgba(255,255,255,0.05)')
)
mono_colors = ['#0284c7', '#0ea5e9', '#38bdf8', '#7dd3fc', '#bae6fd', '#e0f2fe']


# --- Charts Layout: 2 Rows x 3 Columns ---
row1_c1, row1_c2, row1_c3 = st.columns(3)
row2_c1, row2_c2, row2_c3 = st.columns(3)

# 1. Top Left: Line Chart (Month vs Job Count)
with row1_c1:
    df_line = df_filtered.dropna(subset=['Posted_Month']).groupby('Posted_Month').size().reset_index(name='Job Count')
    df_line = df_line.sort_values('Posted_Month')
    
    if not df_line.empty:
        fig1 = px.line(
            df_line, 
            x="Posted_Month", 
            y="Job Count", 
            height=260, 
            markers=True,
            title="Job Postings Over Time", 
            color_discrete_sequence=['#38bdf8']
        )
        
        fig1.update_traces(
            hovertemplate="<b>Posted Date:</b> %{x}<br><b>Job Count:</b> %{y}<extra></extra>"
        )
        
        fig1.update_layout(**chart_layout, xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig1, use_container_width=True)

# 2. Top Middle: Bar Chart (Job Count by Job Title)
with row1_c2:
    df_role = df_filtered.groupby("job_title_short").size().reset_index(name='Job Count')
    df_role = df_role.sort_values(by="Job Count", ascending=False).head(7)
    df_role['Count_Label'] = df_role['Job Count'].apply(lambda x: f"{x/1000:.1f}k".replace('.0k', 'k') if x >= 1000 else str(x))
    
    if not df_role.empty:
        fig2 = px.bar(
            df_role, 
            x="Job Count", 
            y="job_title_short", 
            orientation='h', 
            height=260,
            text="Count_Label",
            title="Job Count by Job Title", 
            color_discrete_sequence=['#0ea5e9']
        )
        
        fig2.update_traces(
            textposition='outside', 
            cliponaxis=False,
            hovertemplate="<b>Job Title</b>: %{y}<br><b>Job Count</b>: %{x}<extra></extra>"
        )
        
        fig2.update_layout(**chart_layout, yaxis_title=None, xaxis_title=None)
        fig2.update_yaxes(categoryorder='total ascending')
        st.plotly_chart(fig2, use_container_width=True)

# 3. Top Right: Pie Chart (Degree vs No Degree)
with row1_c3:
    # Use value_counts() directly on the boolean column
    df_deg = df_filtered["job_no_degree_mention"].value_counts().reset_index()
    df_deg.columns = ['No Degree Mentioned', 'Count']
    
    # 1. SPLIT LABELS: Added <br> for two lines
    df_deg['Degree Req'] = df_deg['No Degree Mentioned'].map({
        True: 'No Degree<br>Mentioned', 
        False: 'Degree<br>Mentioned'
    })
    
    if not df_deg.empty:
        fig3 = px.pie(
            df_deg, 
            names='Degree Req', 
            values='Count', 
            height=260, 
            title="Degree Requirements", 
            color_discrete_sequence=['#0284c7', '#7dd3fc']
        )
        
        fig3.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            hovertemplate="<b>%{label}</b><br>%{percent}<extra></extra>"
        )
        
        fig3.update_layout(**chart_layout, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

# 4. Bottom Left: Scatter Chart (Yearly Median vs Hourly Median by Job Title)
with row2_c1:
    # 1. Group and calculate medians
    df_scat_grp = df_filtered.groupby("job_title_short")[['salary_hour_avg', 'salary_year_avg']].median().reset_index()
    df_scat_grp = df_scat_grp.dropna(subset=['salary_hour_avg', 'salary_year_avg'])
    
    if not df_scat_grp.empty:
        # 2. PRE-FORMAT DATA: This ensures each bubble gets its own correct text
        # Yearly: 150000 -> $150k
        df_scat_grp['Yearly_Label'] = df_scat_grp['salary_year_avg'].apply(
            lambda x: f"${int(x/1000)}k" if x >= 1000 else f"${int(x)}"
        )
        # Hourly: 47.77 -> $47 (using int() to remove decimals without rounding up)
        df_scat_grp['Hourly_Label'] = df_scat_grp['salary_hour_avg'].apply(lambda x: f"${int(x)}")

        # 3. BUILD FIGURE: Pass custom_data INSIDE px.scatter
        fig4 = px.scatter(
            df_scat_grp, 
            x="salary_year_avg", 
            y="salary_hour_avg", 
            color="job_title_short", 
            # This line ensures the correct data is attached to the correct bubble
            custom_data=['job_title_short', 'Yearly_Label', 'Hourly_Label'],
            height=260, 
            trendline="ols", 
            trendline_scope="overall",
            title="Yearly vs Hourly Median Salary",
            color_discrete_sequence=mono_colors
        )
        
        # 4. HOVER TEMPLATE: Use the data passed above
        fig4.update_traces(
            hovertemplate="<b>Job Title</b>: %{customdata[0]}<br>" +
                          "<b>Median Hourly</b>: %{customdata[2]}<br>" +
                          "<b>Median Yearly</b>: %{customdata[1]}" +
                          "<extra></extra>"
        )
        
        fig4.update_layout(
            **chart_layout, 
            showlegend=False, 
            xaxis_title="Median Yearly", 
            yaxis_title="Median Hourly",
            hovermode="closest" # Ensures only the bubble you touch is highlighted
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No dual-salary data available after aggregation.")

# 5. Bottom Middle: Map Chart (Job Count by Country, Monotone Palette)
with row2_c2:
    df_map = df_filtered.groupby("job_country").size().reset_index(name='Job Count')
    if not df_map.empty:
        fig5 = px.choropleth(
            df_map, 
            locations="job_country", 
            locationmode="country names", 
            color="Job Count", 
            # REMOVED: hover_name="job_country" (This stops the double name)
            height=260,
            color_continuous_scale=['#38bdf8', '#0284c7'], 
            title="Job Count by Country"
        )
        
        fig5.update_traces(
            hovertemplate="<b>Job Country</b>: %{location}<br><b>Job Count</b>: %{z}<extra></extra>"
        )
        
        # Make a copy of chart layout and update it for the map specifically
        map_layout = chart_layout.copy()
        map_layout.update(
            margin=dict(l=0, r=0, t=30, b=0), 
            geo=dict(bgcolor='rgba(0,0,0,0)', showland=True, landcolor='#1e293b', showframe=False)
        )
        fig5.update_layout(**map_layout, coloraxis_showscale=False)
        st.plotly_chart(fig5, use_container_width=True)

# 6. Bottom Right: Donut Chart (Experience Level)
with row2_c3:
    df_exp_dist = df_filtered["experience_category"].value_counts().reset_index()
    df_exp_dist.columns = ['Experience', 'Count']
    
    # 1. SPLIT LABELS: Automatically split categories like "Entry Level" into two lines
    df_exp_dist['Experience'] = df_exp_dist['Experience'].str.replace(' ', '<br>')
    
    if not df_exp_dist.empty:
        fig6 = px.pie(
            df_exp_dist, 
            names='Experience', 
            values='Count', 
            hole=0.65, 
            height=260,
            title="Jobs by Experience Level", 
            color_discrete_sequence=mono_colors
        )
        
        # 2. TOUCH/HOVER FIX: Same as the pie chart
        # Shows Bold Label on line 1, Percentage on line 2, and removes extra boxes
        fig6.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            hovertemplate="<b>%{label}</b><br>%{percent}<extra></extra>"
        )
        
        fig6.update_layout(**chart_layout, showlegend=False)
        st.plotly_chart(fig6, use_container_width=True)
