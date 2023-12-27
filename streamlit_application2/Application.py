import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
      # Library of caching in python
from functools import lru_cache
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Superstore!!!", page_icon=":bar_chart:", layout="wide")
st.title(":chart_with_upwards_trend:  Store Sales Analysis Dahsboard")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
fl = st.file_uploader(":file_folder: Upload a file", type=(["csv", "txt", "xlsx", "xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename, encoding="ISO-8859-1")

col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])

# Getting the min and max date
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

st.sidebar.header("Choose your filter: ")
# Create for Region
region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

# Create for State
state = st.sidebar.multiselect("Pick the State", df2["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

# Create for City
city = st.sidebar.multiselect("Pick the City", df3["City"].unique())

# Filter the data based on Region, State and City

if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]

category_df = filtered_df.groupby(by=["Category"], as_index=False)["Sales"].sum()

with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x="Category", y="Sales", text=['${:,.2f}'.format(x) for x in category_df["Sales"]],
                 template="seaborn")
    st.plotly_chart(fig, use_container_width=True, height=200)

with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    fig.update_traces(text=filtered_df["Region"], textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Category.csv", mime="text/csv",
                           help='Click here to download the data as a CSV file')

with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv",
                           help='Click here to download the data as a CSV file')


st.subheader("Hierarchical view of Sales using Sunburst Chart")

# Group the data by Region, Category, and Sub-Category
@lru_cache(maxsize=None)
def sunburst_graph():
    grouped_df = filtered_df.groupby(["Region", "Category", "Sub-Category"]).sum().reset_index()

    # Sort the data by Sales in descending order
    sorted_df = grouped_df.sort_values("Sales", ascending=False)

    # Create a sunburst chart
    fig = px.sunburst(sorted_df, path=["Region", "Category", "Sub-Category"], values="Sales")

    # Update the layout
    fig.update_layout(width=800, height=650)

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
sunburst_graph()
# making the rest of the charts
chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Segment wise Sales')
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    fig.update_traces(text=filtered_df["Segment"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader('Category wise Sales')
    fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
    fig.update_traces(text=filtered_df["Category"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

import plotly.figure_factory as ff

st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = df[0:5][["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
    fig = ff.create_table(df_sample, colorscale="Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data=filtered_df, values="Sales", index=["Sub-Category"], columns="month")
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

# Create a scatter plot
st.subheader("Relationship between Sales and Profits using Scatter Plot")

  # Adding decorator to the function
@lru_cache(maxsize=None)
def scatter_diagram():
    scatter_data = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
    scatter_data['layout'].update(
        title="Relationship between Sales and Profits using Scatter Plot",
        titlefont=dict(size=20),
        xaxis=dict(title="Sales", titlefont=dict(size=19)),
        yaxis=dict(title="Profit", titlefont=dict(size=19))
    )
    import numpy as np
    # Calculate the correlation coefficient
    correlation = np.corrcoef(filtered_df["Sales"], filtered_df["Profit"])[0, 1]
    correlation_text = f"Correlation: {correlation:.2f}"

    # Add correlation information as a text annotation
    scatter_data.add_annotation(
        xref="paper",
        yref="paper",
        x=0.80,
        y=0.05,  # Adjust the y-position here
        text=correlation_text,
        showarrow=False,
        font=dict(size=20),
        align="right"
    )

    # Display the scatter plot in Streamlit
    return st.plotly_chart(scatter_data, use_container_width=True)
scatter_diagram()

# Download orginal DataSet
csv = df.to_csv(index=False).encode('utf-8')
st.download_button('Download Data', data=csv, file_name="Data.csv", mime="text/csv")