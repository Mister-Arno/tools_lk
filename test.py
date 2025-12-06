import streamlit as st
import importlib

# Functies voor je tools
def tool_1():
    st.title("Tool 1: Boomdiagram")
    st.write("Dit is de boomdiagram tool!")
    # Voeg hier je code voor de boomtool in

def tool_2():
    st.title("Tool 2: Ander voorbeeld")
    st.write("Dit is een ander voorbeeld tool!")
    # Voeg hier de code voor een ander tool in

def main():
    # Sidebar voor toolkeuze
    st.sidebar.title("Kies een Tool")
    tool_choice = st.sidebar.radio(
        "Selecteer een tool",
        ("Boomdiagram", "Ander voorbeeld")
    )

    if tool_choice == "Boomdiagram":
        tool_1()
    elif tool_choice == "Ander voorbeeld":
        tool_2()

if __name__ == "__main__":
    main()
