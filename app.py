import streamlit as st
import pandas as pd
from datetime import date
import datetime


def set_page_config() -> None:
    """
    Set the configuration for the Streamlit page.
    """
    st.set_page_config(page_title="Lineare Regression", layout="wide")
    st.markdown(
        """ <style>
    footer {visibility: hidden;}

    footer:hover,  footer:active {
        color: #ffffff;
        background-color: transparent;
        text-decoration: underline;
        transition: 400ms ease 0s;
    }
    </style>""",
        unsafe_allow_html=True,
    )
    hide_decoration_bar_style = """
    <style>
        header {visibility: hidden;}
    </style>
    """
    # st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)


def compute_weekly_summary(dataframe):
    dataframe["Datum"] = pd.to_datetime(dataframe["Datum"]).dt.date
    dataframe["Jahr"] = pd.to_datetime(dataframe["Datum"]).dt.year
    dataframe["Kalenderwoche"] = (
        pd.to_datetime(dataframe["Datum"]).dt.isocalendar().week
    )
    summary = (
        dataframe.groupby(["Jahr", "Kalenderwoche"])
        .agg(
            Arbeitszeit_Gesamt=pd.NamedAgg(column="Arbeitszeit", aggfunc="sum"),
            Anzahl_Autofahrten=pd.NamedAgg(column="Auto", aggfunc="sum"),
        )
        .reset_index()
    )
    return summary


set_page_config()

# Titel
st.title("Arbeitszeit")

# Inputs
input_time = st.time_input("Arbeitszeit", datetime.time(8))
work_time = (
    input_time.hour + input_time.minute / 60
)  # Convert to a float representing hours
car = st.checkbox("Mit Auto gefahren")
selected_date = st.date_input("Datum", date.today())
selected_date = pd.Timestamp(selected_date)


# Speichern
log_file = "work_log.csv"

try:
    df = pd.read_csv(log_file)

except FileNotFoundError:
    df = pd.DataFrame(columns=["Arbeitszeit", "Auto", "Datum"])

df["Datum"] = pd.to_datetime(df["Datum"]).dt.date
df["Jahr"] = pd.to_datetime(df["Datum"]).dt.year
df["Kalenderwoche"] = pd.to_datetime(df["Datum"]).dt.isocalendar().week


if st.button("Eintragen"):
    new_entry = {
        "Arbeitszeit": work_time,
        "Auto": car,
        "Datum": selected_date.date(),
        "Jahr": selected_date.year,
        "Kalenderwoche": selected_date.isocalendar().week,
    }
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(log_file, index=False)
    st.success("Eintrag erfolgreich gespeichert!")

weekly_summary = (
    df.groupby(["Jahr", "Kalenderwoche"])
    .agg(
        Total_Arbeitszeit=pd.NamedAgg(column="Arbeitszeit", aggfunc="sum"),
        Anzahl_Autofahrten=pd.NamedAgg(column="Auto", aggfunc="sum"),
    )
    .reset_index()
)

# Anzeige
st.subheader("Erfasste Daten:")
edited_data = st.data_editor(df, hide_index=True)
if st.button("Änderungen speichern"):
    # Speichere die bearbeiteten Daten in die CSV-Datei
    edited_data.to_csv(log_file, index=False)

    # Lade die Daten erneut
    df = pd.read_csv(log_file)
    df["Datum"] = pd.to_datetime(df["Datum"]).dt.date
    df["Jahr"] = pd.to_datetime(df["Datum"]).dt.year
    df["Kalenderwoche"] = pd.to_datetime(df["Datum"]).dt.isocalendar().week

    # Erneute Berechnung der Zusammenfassung
    weekly_summary = (
        df.groupby(["Jahr", "Kalenderwoche"])
        .agg(
            Total_Arbeitszeit=pd.NamedAgg(column="Arbeitszeit", aggfunc="sum"),
            Anzahl_Autofahrten=pd.NamedAgg(column="Auto", aggfunc="sum"),
        )
        .reset_index()
    )
    st.success("Änderungen erfolgreich gespeichert!")


week_time = df[
    df["Datum"].between(
        (selected_date - pd.Timedelta(days=6)).date(), selected_date.date()
    )
]["Arbeitszeit"].sum()

car_rides = df[df["Auto"] == True].shape[0]

st.subheader("Zusammenfassung pro Kalenderwoche:")
st.dataframe(weekly_summary)
