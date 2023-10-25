import streamlit as st
from eda import * 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
from shapely.geometry import Point
from geopandas import GeoDataFrame
from babel.numbers import format_currency
import textwrap

def wrap_labels(ax, width, break_long_words=False):
    labels = []
    for label in ax.get_xticklabels():
        text = label.get_text()
        labels.append(textwrap.fill(text, width=width,
                      break_long_words=break_long_words))
    ax.set_xticklabels(labels, rotation=0)


min_date = pd.to_datetime(orders["order_purchase_timestamp"].min())
max_date = pd.to_datetime(orders["order_purchase_timestamp"].max())

menu = "Home📊"
with st.sidebar:
    col1, col2, col3 = st.columns([2,6,1])
    with col1:
        st.write("")
    with col2:
        st.image("store.png",width=150)
    with col3:
        st.write("")
    menu = st.radio('Menu', options=['Home📊','Products👕', 'Users🧑'])

if menu == "Home📊":
    st.write("""
        # Analisis Data E-commerce!📊
    """)

    #st.dataframe(data_revenue)

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
    st.write(f"""
    ### Pendapatan dari {start_date} sampai {end_date}
    """)
    data_revenue = revenue(start_date,end_date)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Orders", value="{:,.2f}".format(data_revenue["order"].sum()))
    with col2:
        currency = format_currency(data_revenue["revenue"].sum(), "BRL", locale='pt_BR') 
        st.metric("Revenue", value=currency)

    fig, ax = plt.subplots(figsize=(15, 5))
    ax.plot(data_revenue["date"], data_revenue["order"], marker='o', linewidth=2)
    st.pyplot(fig)

    st.write(f"""
    ### Order terbaru
    """)
    newest_date, newest_value = newest_order()
    col1, col2= st.columns(2)
    with col1:
        st.metric("Date", value=newest_date)
    with col2:
        st.metric("Value", value=newest_value)

    asc = False
    st.write("""*Filter untuk tabel dibawah*""")
    col1, col2 = st.columns(2)
    with col1:
        range = st.slider(
            'Range Table', 0, 100, 5
        )
    with col2:
        genre = st.radio(
            label="Urutkan",
            options=('Atas', 'Bawah'),
        horizontal=False
        )
        if genre == "Atas":
            asc = False
        elif genre == "Bawah":
            asc = True

    st.write(f"""
    ### Barang dengan penghasilan terbesar
    """)
    product_rev = product_revenue(asc)
    col1, col2, col3= st.columns(3)
    with col1:
        st.metric("Rata-rata", value="{:,.2f}".format(product_rev["revenue"].mean()))
    with col2:
        st.metric("Paling besar", value="{:,.2f}".format(product_rev["revenue"].max()))
    with col3:
        st.metric("Paling kecil", value="{:,.2f}".format(product_rev["revenue"].min()))
    st.dataframe(product_rev.head(5), width=700)
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(x="revenue", y="category", data=product_rev.head(),
                label="Total", palette=colors)
    st.pyplot(fig)

    st.write(f"""
    ### Order terbanyak 
    """)
    list_order = order(asc)
    col1, col2, col3= st.columns(3)
    with col1:
        st.metric("Rata-rata", value="{:,.2f}".format(list_order["value"].mean()))
    with col2:
        st.metric("Paling besar", value="{:,.2f}".format(list_order["value"].max()))
    with col3:
        st.metric("Paling kecil", value="{:,.2f}".format(list_order["value"].min()))
    st.dataframe(list_order.head(range), width=700)

    st.write(f"""
    ### Ongkir terbesar 
    """)
    list_freight = freight(asc)
    col1, col2, col3= st.columns(3)
    with col1:
        st.metric("Rata-rata", value="{:,.2f}".format(list_freight["freight"].mean()))
    with col2:
        st.metric("Paling besar", value="{:,.2f}".format(list_freight["freight"].max()))
    with col3:
        st.metric("Paling kecil", value="{:,.2f}".format(list_freight["freight"].min()))
    st.dataframe(list_freight.head(range), width=700)


    st.write("""
    ### Metode Pembayaran
    """)
    method = payment_type()
    fig, ax = plt.subplots(figsize=(5, 5))
    palette_color = sns.color_palette('bright')
    ax.pie(method.total, labels=method.method, colors=palette_color, explode=method.total/1000000, autopct='%.0f%%')
    st.pyplot(fig)

    st.dataframe(method.head(), width=700)

if menu == "Products👕":
    st.write("""
    # About Products👕
    """)
    st.write("""*Aktifkan filter untuk mengatur data*""")
    filter = st.checkbox('Filter')
    asc = False
    table = False
    range = 0
    if filter:
        col1, col2 = st.columns(2)

        with col1:
            table = st.checkbox('Show Table')
            range = st.slider(
                'Range Table', 0, 100, 5
            )
        with col2:
            genre = st.radio(
                label="Urutkan",
                options=('Atas', 'Bawah'),
            horizontal=False
            )
            if genre == "Atas":
                asc = False
            elif genre == "Bawah":
                asc = True

        
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Weight⚖️", "Favorit🛒", "Quantity🧮",
                                                "Price🏷️","Size📐","Rating⭐"])
    with tab1:
        st.header("Berdasarkan Berat⚖️")
        product_weight = weight(asc)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rata-rata", value="{:,.2f}".format(product_weight["weight"].mean()))
        with col2:
            st.metric("Paling Berat", value="{:,.2f}".format(product_weight["weight"].max()))
        with col3:
            st.metric("Paling Ringan", value="{:,.2f}".format(product_weight["weight"].min()))

        if table:
            st.dataframe(product_weight.head(range), width=700)

        fig, ax = plt.subplots(figsize=(10, 5))
        colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
        sns.barplot(x="category", y="weight", data=product_weight.head(),
                    label="Weight", palette=colors)
        wrap_labels(ax, 10)
        st.pyplot(fig)
    
    with tab2:
        st.header("Berdasarkan Penjualan🛒")
        product_favorit = favorit(asc)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rata-rata", value="{:,.2f}".format(product_favorit["total"].mean()))
        with col2:
            st.metric("Paling Banyak", value="{:,.2f}".format(product_favorit["total"].max()))
        with col3:
            st.metric("Paling Sedikit", value="{:,.2f}".format(product_favorit["total"].min()))

        if table:
            st.dataframe(product_favorit.head(range), width=700)
    
        fig, ax = plt.subplots(figsize=(10, 5))
        colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
        sns.barplot(x="category", y="total", data=product_favorit.head(),
                    label="Total", palette=colors)
        wrap_labels(ax, 10)
        st.pyplot(fig)

    with tab3:
        st.header("Berdasarkan Kuantitas🧮")
        product_quantity = quantity(asc)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rata-rata", value="{:,.2f}".format(product_quantity["total"].mean()))
        with col2:
            st.metric("Paling Banyak", value="{:,.2f}".format(product_quantity["total"].max()))
        with col3:
            st.metric("Paling Sedikit", value="{:,.2f}".format(product_quantity["total"].min()))

        if table:
            st.dataframe(product_quantity.head(range), width=700)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
        sns.barplot(x="category", y="total", data=product_quantity.head(),
                    label="Total", palette=colors)
        wrap_labels(ax, 10)
        st.pyplot(fig)
        

    with tab4:
        st.header("Berdasarkan Harga🏷️")
        product_price = price(asc)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rata-rata", value="{:,.2f}".format(product_price["price"].mean()))
        with col2:
            st.metric("Paling Mahal", value="{:,.2f}".format(product_price["price"].max()))
        with col3:
            st.metric("Paling Murah", value="{:,.2f}".format(product_price["price"].min()))

        if table:
            st.dataframe(product_price.head(range), width=700)

        fig, ax = plt.subplots(figsize=(10, 5))
        colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
        sns.barplot(x="category", y="price", data=product_price.head(),
                    label="Price", palette=colors)
        wrap_labels(ax, 10)
        st.pyplot(fig)

    with tab5:
        st.header("Berdasarkan Ukuran📐")
        product_size = size(asc)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rata-rata", value="{:,.2f}".format(product_size["volume"].mean()))
        with col2:
            st.metric("Paling Besar", value="{:,.2f}".format(product_size["volume"].max()))
        with col3:
            st.metric("Paling Kecil", value="{:,.2f}".format(product_size["volume"].min()))

        if table:
            st.dataframe(product_size.head(range), width=700)

        fig, ax = plt.subplots(figsize=(10, 5))
        colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
        sns.barplot(x="category", y="volume", data=product_size.head(),
                    label="Volume", palette=colors)
        wrap_labels(ax, 10)
        st.pyplot(fig)

    with tab6:
        st.header("Berdasarkan Rating⭐")
        product_rating = rating(asc)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rata-rata", value="{:,.2f}".format(product_rating["review_score"].mean()))
        with col2:
            st.metric("Paling Tinggi", value="{:,.2f}".format(product_rating["review_score"].max()))
        with col3:
            st.metric("Paling Rendah", value="{:,.2f}".format(product_rating["review_score"].min()))

        if table:
            st.dataframe(product_rating.head(range), width=700)

        fig, ax = plt.subplots(figsize=(10, 5))
        colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
        sns.barplot(x="category", y="review_score", data=product_rating.head(),
                    label="Score", palette=colors)
        wrap_labels(ax, 10)
        st.pyplot(fig)

if menu == "Users🧑":
    st.write("""
        # About Users🧑
    """)

    table = st.checkbox('Show Table')
    range = st.slider(
        'Range Table', 0, 100, 5
    )
    asc = False
    genre = st.radio(
        label="Urutkan",
        options=('Atas', 'Bawah'),
    horizontal=True
    )
    if genre == "Atas":
        asc = False
    elif genre == "Bawah":
        asc = True
    
    st.header("Pembeli berdasarkan kota")
    data_customer = customer(asc)
    if table:
        st.dataframe(data_customer.head(range), width=700)
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(x="customers", y="city", data=data_customer.head(5),
                label="Total", palette=colors)
    st.pyplot(fig)

    st.header("Penjual berdasarkan kota")
    data_seller = seller(asc)
    if table:
        st.dataframe(data_seller.head(range), width=700)
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(x="seller", y="city", data=data_seller.head(5),
                label="Total", palette=colors)
    st.pyplot(fig)

    st.header("Demographic pengguna")
    geographical = st.checkbox('Lihat demographic pengguna')

    if geographical:

        geometry = [Point(xy) for xy in zip(geo['geolocation_lng'], geo['geolocation_lat'])]
        gdf = GeoDataFrame(geo, geometry=geometry)

        fig, ax = plt.subplots(1, figsize=(8,10))
        ax.set_axis_on()

        # #this is a simple map that goes with geopandas
        brazil = gpd.read_file("brazil/gadm36_BRA_1.shp")
        gdf.plot(ax=brazil.plot(ax=ax,cmap='YlOrRd'), marker='o', color='red', markersize=2);


        points = brazil.copy()
        # change the geometry
        points.geometry = points['geometry'].centroid
        # Plot the labels
        for x, y, label in zip(points.geometry.x, points.geometry.y, points.NAME_1):
            ax.annotate(label, xy=(x, y), xytext=(3, 3), alpha=1, textcoords="offset points",color='black')
        st.pyplot(fig)
