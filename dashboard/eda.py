# import library
import pandas as pd

customers = pd.read_csv("./data/customers.csv")
geo = pd.read_csv("./data/geo.csv")
orders = pd.read_csv("./data/orders.csv")
order_items = pd.read_csv("./data/order_items.csv")
order_payments = pd.read_csv("./data/order_payments.csv")
order_reviews = pd.read_csv("./data/order_reviews.csv")
products = pd.read_csv("./data/products.csv")
product_cat = pd.read_csv("./data/product_cat.csv")
sellers = pd.read_csv("./data/sellers.csv")

# Customer
def customer(asc):
    query = "customer_city"
    customers_df = pd.DataFrame(customers.groupby(by=query).customer_unique_id.nunique().sort_values(ascending=asc)).reset_index()
    customers_df.columns=["city","customers"]
    return customers_df

# Seller
def seller(asc):
    query = "seller_city"
    seller_df = pd.DataFrame(sellers.groupby(by=query).seller_id.nunique().sort_values(ascending=asc)).reset_index()
    seller_df.columns=["city","seller"]
    return seller_df

# Urutan harga
def price(asc):
    order = order_items[["product_id","price"]]
    price = order.merge(products,on="product_id")
    price = price[["product_category_name","price"]]
    price.columns = ["category","price"]
    price.reset_index(drop=True,inplace=True)
    return price.sort_values(by="price",ascending=asc)

# Urutan berat
def weight(asc):
  weight = products.sort_values(by="product_weight_g",ascending=asc)
  weight = weight[["product_category_name","product_weight_g"]]
  weight.columns = ["category","weight"]
  weight.reset_index(drop=True,inplace=True)
  return weight

# Urutan ukuran
def size(asc):
    product_volume = products[["product_category_name","product_length_cm","product_height_cm","product_width_cm"]]
    product_volume["volume"] = product_volume["product_length_cm"] * product_volume["product_height_cm"] * product_volume["product_width_cm"]
    product_volume = product_volume.sort_values(by="volume",ascending=asc)
    product_volume = product_volume[["product_category_name","volume"]]
    product_volume.columns = ["category","volume"]
    product_volume.reset_index(drop=True,inplace=True)
    return product_volume

# Urutan harga
def quantity(asc):
    product_for_sale = products.groupby("product_category_name").product_id.nunique().reset_index()
    product_for_sale.columns = ["category","total"]
    product_for_sale = product_for_sale.sort_values(by="total",ascending=asc)
    product_for_sale.reset_index(drop=True,inplace=True)
    return product_for_sale

# Urutan favorit
def favorit(asc):
    sell = order_items.groupby("product_id").order_id.nunique().reset_index()
    sell.columns = ["product_id","total"]
    sell = sell.sort_values(by="total",ascending=False)
    # Gabungkan data sell dengan table product untuk mendapatkan namanya
    df_sell = sell.merge(products,on="product_id")
    # Karena dalam satu category bisa terdapat beberapa product kiat gabungkan ke dalam satu kategori saja
    # Karena kita tidak punya nama product, hanya ada kategori
    # Kita groupby "kategori" dan tambahkan semua totalnya
    df_sell = df_sell.groupby("product_category_name").total.sum().reset_index().sort_values(by="total",ascending=asc)
    df_sell.columns = ["category","total"]
    df_sell.reset_index(drop=True,inplace=True)
    return df_sell

# Urutan rating
def rating(asc):
    df_rating = order_reviews.merge(order_items,on="order_id")
    df_rating = df_rating[["order_id","review_score","product_id","review_answer_timestamp"]]
    df_rating = df_rating.merge(products,on="product_id")
    df_rating = df_rating[["order_id","review_score","product_id","product_category_name","review_answer_timestamp"]]
    df_rating = df_rating.groupby("product_category_name").review_score.mean().reset_index().sort_values(by="review_score",ascending=asc)
    df_rating.columns = ["category","review_score"]
    df_rating.reset_index(drop=True,inplace=True)
    return df_rating

# Metode pembayaran
def payment_type():
  method = order_payments.merge(orders,on="order_id")[["order_id","payment_type","order_purchase_timestamp"]]
  # Gunakan kondisi terhadap kolom order_purchase_timestamp
  # method = method[method.order_purchase_timestamp >= ??]
  method = order_payments.groupby("payment_type").order_id.nunique().reset_index()
  method.columns = ["method","total"]
  method = method.sort_values(by="total",ascending=False)
  method.reset_index(drop=True,inplace=True)
  return method


# Urutan ongkir
def freight(asc):
    # Gunakan kondisi terhadap kolom shipping_limit_date
    # freight = order_items[order_items.shipping_limit_date >= ??]
    freight = order_items[["shipping_limit_date","price","freight_value"]]
    freight = freight.sort_values(by="freight_value",ascending=asc)
    freight.columns = ["date","price","freight"]
    freight.reset_index(drop=True,inplace=True)
    return freight


# Pembayaran terbesar
def order(asc):
    highest = order_payments.merge(orders,on="order_id").reset_index()
    # kondisi terhadap kolom order_purchase_timestamp
    # highest = highest[highest.order_purchase_timestamp >= ??]
    highest = highest.sort_values(by="payment_value",ascending=asc)[["order_purchase_timestamp","payment_value"]]
    highest.columns = ["date","value"]
    highest.reset_index(drop=True,inplace=True)
    return highest

# Order terbaru
def newest_order():
  newest_order_date = orders.order_purchase_timestamp.max()
  newest_order_id = orders[orders.order_purchase_timestamp >= newest_order_date]["order_id"].iloc[0]
  newest_order_value = order_payments[order_payments.order_id == newest_order_id]["payment_value"].iloc[0]
  return newest_order_date,newest_order_value


# hitung data yang berhasil terjual
def revenue(start_date,end_date):
  df_orders = orders.query("order_status != 'canceled' & order_status != 'unavailable'")
  df_orders = df_orders.merge(order_items,on="order_id")
  df_orders["order_purchase_timestamp"] = pd.to_datetime(df_orders["order_purchase_timestamp"])
  daily_orders_df = df_orders.resample(rule="D", on='order_purchase_timestamp').agg({
          "order_id": "nunique",
          "price": "sum"
      }).reset_index()
  daily_orders_df.columns = ["date","order","revenue"]
  daily_orders_df = daily_orders_df.sort_values(by="date")
# daily_orders_df.date = daily_orders_df.date.strftime('%B') #mengubah format order date menjadi nama bulan
  daily_orders_df = daily_orders_df[(daily_orders_df["date"] >= str(start_date)) &
                    (daily_orders_df["date"] <= str(end_date))]
  daily_orders_df.reset_index(drop=True,inplace=True)
  return daily_orders_df

def product_revenue(asc):
  df_revenue = order_items.merge(products,on="product_id")
  df_revenue = df_revenue[["shipping_limit_date","product_id","price","product_category_name"]]
  df_revenue = df_revenue.groupby("product_category_name").price.sum().reset_index()
  df_revenue = df_revenue.sort_values(by="price",ascending=asc)
  df_revenue.columns = ["category","revenue"]
  df_revenue.reset_index(drop=True,inplace=True)
  return df_revenue




