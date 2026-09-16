import streamlit as st
import datetime
import pandas as pd
import statsapi

st.set_page_config(
    page_title="MLB Universal Numerology Alignments",
    page_icon="⚾",
    layout="wide"
)

# ---------------------------------------------------------
# NUMEROLOGY HELPER FUNCTIONS
# ---------------------------------------------------------
def get_digital_root(n):
    """Calculates single-digit digital root (1-9) of an integer."""
    try:
        n = int(n)
        if n == 0:
            return 0
        root = n % 9
        return 9 if root == 0 else root
    except (ValueError, TypeError):
        return None

def reduce_date_str(date_obj):
    """Calculates universal day root from a date object."""
    month_root = get_digital_root(date_obj.month)
    day_root = get_digital_root(date_obj.day)
    year_root = get_digital_root(date_obj.year)
    return get_digital_root(month_root + day_root + year_root)

def get_personal_day(birth_date_str, universal_day_root):
    """Calculates Personal Day: Birth Month + Birth Day + Universal Day Root."""
    try:
        bdate = datetime.datetime.strptime(birth_date_str, "%Y-%m-%d")
        b_month_root = get_digital_root(bdate.month)
        b_day_root = get_digital_root(bdate.day)
        total = b_month_root + b_day_root + universal_day_root
        return get_digital_root(total)
    except Exception:
        return None

def get_vibrational_family(jersey_num):
    """Categorizes player into a Vibrational Family based on jersey root/raw value."""
    try:
        j_int = int(jersey_num)
        if j_int in [11, 22, 33]:
            return "Master Number Family (11, 22, 33)"
        
        root = get_digital_root(j_int)
        families = []
        if root in [1, 5, 7]:
            families.append("Mind & Thought (1, 5, 7)")
        if root in [3, 5, 6]:
            families.append("Creation (3, 5, 6)")
        if root in [2, 4, 8]:
            families.append("Manifestation (2, 4, 8)")
        if root in [1, 8, 9]:
            families.append("Humanitarian (1, 8, 9)")
        
        return ", ".join(families) if families else "Other"
    except (ValueError, TypeError):
        return "Unknown"

# ---------------------------------------------------------
# DATA FETCHING (MLB STATS API)
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_active_batters():
    """Fetches active batters across all 30 MLB teams."""
    teams = statsapi.get('teams', {'sportId': 1})['teams']
    player_list = []
    
    progress_bar = st.progress(0)
    total_teams = len(teams)
    
    for idx, team in enumerate(teams):
        team_id = team['id']
        team_name = team['name']
        
        try:
            roster = statsapi.get('team_roster', {'teamId': team_id, 'rosterType': 'active'})['roster']
            for entry in roster:
                person = entry.get('person', {})
                pos = entry.get('position', {}).get('abbreviation', '')
                
                # Filter out Pitchers (P, TWP, etc. if desired)
                if pos != 'P':
                    p_id = person.get('id')
                    try:
                        detail = statsapi.get('person', {'personId': p_id})['people'][0]
                        birth_date = detail.get('birthDate', None)
                        jersey = detail.get('primaryNumber', entry.get('jerseyNumber', None))
                        name = detail.get('fullName', person.get('fullName'))
                        
                        if birth_date and jersey is not None:
                            player_list.append({
                                'Player': name,
                                'Team': team_name,
                                'Position': pos,
                                'Jersey': str(jersey),
                                'BirthDate': birth_date
                            })
                    except Exception:
                        continue
        except Exception:
            pass
        
        progress_bar.progress((idx + 1) / total_teams)
        
    progress_bar.empty()
    return pd.DataFrame(player_list)

# ---------------------------------------------------------
# UI APP LAYOUT
# ---------------------------------------------------------
st.title("⚾ MLB Universal Numerology Alignment Engine")
st.markdown("Analyze active MLB batters based on **Universal Day**, **Calendar Root**, **Personal Day**, and **Vibrational Family** groupings.")

# Date Selector Sidebar
st.sidebar.header("Target Date Selection")
selected_date = st.sidebar.date_input("Select Game Date", datetime.date.today())

# Dynamic Date Calculations
universal_day = reduce_date_str(selected_date)
calendar_day_root = get_digital_root(selected_date.day)

# Display Key Date Indicators
col1, col2, col3 = st.columns(3)
col1.metric("Selected Date", selected_date.strftime("%B %d, %Y"))
col2.metric("Universal Day Root", universal_day)
col3.metric("Calendar Day Root", calendar_day_root)

# Load Active Player Roster
st.write("### Loading Active Batter Data...")
df = fetch_active_batters()

if not df.empty:
    # Perform Mathematical Transformations
    df['Jersey_Root'] = df['Jersey'].apply(get_digital_root)
    df['Personal_Day'] = df['BirthDate'].apply(lambda bd: get_personal_day(bd, universal_day))
    df['Vibrational_Family'] = df['Jersey'].apply(get_vibrational_family)

    st.success(f"Successfully loaded {len(df)} active batters!")

    # Tabbed Interface
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Group 1: Universal Day Alignment",
        "📅 Group 2: Calendar Root Alignment",
        "✨ Group 3: Personal Day Alignment",
        "🏛 Group 4: Vibrational Family Matrix"
    ])

    # ---------------------------------------------------------
    # TAB 1: Universal Day Alignment
    # ---------------------------------------------------------
    with tab1:
        st.subheader(f"Group 1: Universal Day Alignments (Target Root: {universal_day})")
        st.markdown(f"Players whose **Jersey Number Digital Root** matches today's Universal Day Number (**{universal_day}**).")
        
        u_align_df = df[df['Jersey_Root'] == universal_day]
        st.metric("Total Players Aligned", len(u_align_df))
        st.dataframe(u_align_df[['Player', 'Team', 'Position', 'Jersey', 'BirthDate', 'Jersey_Root']], use_container_width=True)

    # ---------------------------------------------------------
    # TAB 2: Calendar Root Alignment
    # ---------------------------------------------------------
    with tab2:
        st.subheader(f"Group 2: Calendar Day Root Alignments (Target Root: {calendar_day_root})")
        st.markdown(f"Players whose **Jersey Number Digital Root** matches the Day of the Month Root (**{calendar_day_root}**).")
        
        c_align_df = df[df['Jersey_Root'] == calendar_day_root]
        st.metric("Total Players Aligned", len(c_align_df))
        st.dataframe(c_align_df[['Player', 'Team', 'Position', 'Jersey', 'BirthDate', 'Jersey_Root']], use_container_width=True)

    # ---------------------------------------------------------
    # TAB 3: Personal Day Alignment
    # ---------------------------------------------------------
    with tab3:
        st.subheader("Group 3: Personal Day Alignments")
        st.markdown("Players whose **Personal Day Number** (Birth Month + Birth Day + Universal Day) matches the target universal root or selected filter.")
        
        target_pd = st.slider("Select Target Personal Day Root", 1, 9, universal_day)
        p_align_df = df[df['Personal_Day'] == target_pd]
        
        st.metric(f"Total Players on Personal Day {target_pd}", len(p_align_df))
        st.dataframe(p_align_df[['Player', 'Team', 'Position', 'Jersey', 'BirthDate', 'Personal_Day']], use_container_width=True)

    # ---------------------------------------------------------
    # TAB 4: Vibrational Family Subgroups
    # ---------------------------------------------------------
    with tab4:
        st.subheader("Group 4: Vibrational Family Subgroups")
        st.markdown("Categorizes all players by their jersey number's alignment to core numerology families.")
        
        family_option = st.selectbox("Select Family Group", [
            "All",
            "Mind & Thought (1, 5, 7)",
            "Creation (3, 5, 6)",
            "Manifestation (2, 4, 8)",
            "Humanitarian (1, 8, 9)",
            "Master Number Family (11, 22, 33)"
        ])
        
        if family_option != "All":
            fam_df = df[df['Vibrational_Family'].str.contains(family_option, regex=False, na=False)]
        else:
            fam_df = df
            
        st.dataframe(fam_df[['Player', 'Team', 'Position', 'Jersey', 'Vibrational_Family', 'Jersey_Root']], use_container_width=True)

else:
    st.error("Unable to load active roster data from the MLB Stats API.")
