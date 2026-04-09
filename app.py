import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import calendar

# 1. Configuration de la page
st.set_page_config(page_title="VTC Expenses Tracker", layout="wide")

@st.cache_data
def load_and_clean_data():
    df = pd.read_csv('mon_historique_gozem.csv')
    df['jour'] = pd.to_datetime(df['jour'], dayfirst=True)
    df['jours'] = df['jour'].dt.day
    df['mois'] = df['jour'].dt.month
    df['annees'] = df['jour'].dt.year
    df['remise'] = df['total_fcfb'] - df['montant_paye']
    df.loc[(df['type_vehicule'] == 'Clim') | (df['type_vehicule'] == 'Basic'), 'type_trans'] = 'v'
    df.loc[(df['type_vehicule'] == 'Zem') | (df['type_vehicule'] == 'VIP'), 'type_trans'] = 'm'
    #df_id_course_inconnu = df[df['id_course'].isnull()]
    df['prix_au_km'] = df['montant_paye'] / df['distance_km'].replace(0, np.nan)
    df.dropna(subset=['id_course'], inplace=True)
    df['duree_min'] = df['duree_min'].fillna(0)
    df['mois_nom'] = df['mois'].apply(lambda x: calendar.month_name[int(x)])
    df['jour_nom'] = df['jour'].dt.day_name(locale='French')
    df['jour_nom'] = df['jour_nom'].astype(str).str.strip().str.capitalize()
    return df

df = load_and_clean_data()
# 2. --- BARRE LATERALE (Filtres globaux) ---
st.sidebar.title("📌 Filtres")
annee_filter = st.sidebar.multiselect("Année", options=df['annees'].unique(), default=df['annees'].unique())
type_filter = st.sidebar.multiselect("Type de Transport", options=df['type_trans'].unique(), default=df['type_trans'].unique())

df_filtered = df[(df['annees'].isin(annee_filter)) & (df['type_trans'].isin(type_filter))]

# 3. --- MISE EN PAGE PAR ONGLETS ---
st.title("🚖 Dashboard VTC Global")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["💰 Finance", "🕒 Temps & Habitudes", "🚗 Véhicules & Chauffeurs", "📋 Données Brutes", "Liste"])

# --- ONGLET 1 : FINANCE ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Météo Financière Mensuelle")
        fig1 = px.bar(df_filtered.groupby('mois_nom')['montant_paye'].sum().reset_index(), x='mois_nom', y='montant_paye')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("Evolution du prix au KM")
        ordre_en = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        df_km = df_filtered.groupby('mois_nom')['prix_au_km'].mean().reindex(ordre_en).dropna().reset_index()
        fig8 = px.line(df_km, x='mois_nom', y='prix_au_km', markers=True)
        st.plotly_chart(fig8, use_container_width=True)

# --- ONGLET 2 : TEMPS ET HABITUDES ---
with tab2:
    st.subheader("Matrice de l'heure de pointe (Heatmap)")
    df['jour_nom'] = df['jour_nom'].astype(str).str.strip().str.capitalize()
    df['heure'] = pd.to_numeric(df['heure'], errors='coerce').fillna(0).astype(int)
    df['montant_paye'] = pd.to_numeric(df['montant_paye'], errors='coerce').fillna(0)
    ordre_jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    fig7 = px.density_heatmap(df_filtered, x="heure", y="jour_nom", z="montant_paye", histfunc="avg", 
                              category_orders={"jour_nom": ordre_jours}, color_continuous_scale="YlOrRd")
    st.plotly_chart(fig7, use_container_width=True)

    st.subheader("Corrélation Distance vs Durée")
    fig9 = px.scatter(df_filtered, x='distance_km', y='duree_min', color='montant_paye', size='montant_paye')
    st.plotly_chart(fig9, use_container_width=True)

with tab3:
    st.subheader("Score de Satisfaction Moyen")
    note_moy = df_filtered['note_chauffeur'].mean()
    fig6 = go.Figure(go.Indicator(mode="gauge+number", value=note_moy, gauge={'axis': {'range': [None, 5]}}))
    st.plotly_chart(fig6, use_container_width=True)

with tab4:
    st.subheader("CA par type de Transport")
    fig11 = px.pie(df_filtered, values='montant_paye', names='type_trans', hole=0.3)
    st.plotly_chart(fig11, use_container_width=True)

    st.subheader("CA par type de Véhicule")
    fig11 = px.pie(df_filtered, values='montant_paye', names='type_vehicule', hole=0.3)
    st.plotly_chart(fig11, use_container_width=True)

with tab5:
    st.subheader("Top 10 des trajets les plus chers")
    st.table(df_filtered.sort_values('montant_paye', ascending=False).head(10)[['jour', 'chauffeur', 'distance_km', 'montant_paye']])


    st.subheader("Top 10 : Chauffeurs Fréquents")
    # --- VOTRE CODE DASHBOARD 5 INTÉGRÉ ---
    df_chauffeurs = df_filtered['chauffeur'].value_counts().reset_index()
    df_chauffeurs.columns = ['chauffeur', 'nombre_de_courses']
    df_top10 = df_chauffeurs.head(10)

    fig5 = px.bar(
           df_top10, 
           x='nombre_de_courses', 
           y='chauffeur',
           orientation='h',
           color='nombre_de_courses',
           color_continuous_scale='Blues',
           text_auto=True,
           labels={'nombre_de_courses': 'Trajets', 'chauffeur': 'Chauffeur'}
        )
    fig5.update_yaxes(autorange="reversed")
    fig5.update_layout(showlegend=False, template='plotly_white')
        
    st.plotly_chart(fig5, use_container_width=True)