import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

## Add text elements
st.title('Somehow cool Penguins explorer')

#The text can be formatted with markdown
st.write('Demo little app with our _beloved_ **penguins dataset** to learn about `streamlit` functionality')

st.header('The Data')
st.write('The palmer penguins data set containing measurements of penguins of different species.')
st.image('lter_penguins.png')

df = pd.read_csv('penguins_pimped.csv')
df.dropna(inplace=True)
st.write('Beautiful data display of data frames')
st.write(df.sample(10))

## Add interactive elements
species = st.selectbox('Which species do you want to see?', df['species'].unique())


st.subheader(f'A small sample of the {species} penguins')
df_species = df.loc[df['species'] == species, df.columns]
if st.checkbox('Show me the sample'):
    st.write(df_species)

## Plotting!
st.header('Plots!')
st.subheader('Native streamlit plots')
st.write('Pass a fitting data format to the plot for easy display. Useful for `group.by()` etc')
st.bar_chart(data = df.groupby('species')['island'].count())

st.subheader('Matplotlib & Co')
fig, ax = plt.subplots()
ax = sns.scatterplot(data = df, x = 'body_mass_g', y = 'flipper_length_mm', hue = 'species')
sns.despine()
st.pyplot(fig)


st.subheader('Plotly plots')
fig = px.scatter(df,
                x = 'bill_length_mm',
                y = 'bill_depth_mm',
                animation_frame = 'species',
                range_x = [30, 65],
                range_y = [10,25],
                color = 'sex',
                hover_name = 'name' )
st.plotly_chart(fig)

## Maps

st.header('Maps')
st.subheader('Super easy with `st.map`')
st.write('You need to have columns in your data frame named `lon` and `lat` with coordinates')
st.map(df)
st.write('For more sophisicated maps check [`pydeck`](https://deckgl.readthedocs.io/en/latest/)')