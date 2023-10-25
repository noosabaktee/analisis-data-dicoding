# import library
import pandas as pd

customers = pd.read_csv("../data/customers_dataset.csv")
geolocation = pd.read_csv("../data/geolocation_dataset.csv")
orders = pd.read_csv("../data/orders_dataset.csv")
order_items = pd.read_csv("../data/order_items_dataset.csv")
order_payments = pd.read_csv("../data/order_payments_dataset.csv")
order_reviews = pd.read_csv("../data/order_reviews_dataset.csv")
products = pd.read_csv("../data/products_dataset.csv")
sellers = pd.read_csv("../data/sellers_dataset.csv")

table = [customers,geolocation,orders,order_items,order_items,order_payments,order_reviews,products,sellers]
table_name = ["customers","geolocation","orders","order_items","order_items","order_payments","order_reviews","products","sellers"]

# Delete duplicate data
geolocation.drop_duplicates(inplace=True)

indexData = products[products.product_weight_g.isna() == True].index
# Satu product bernama bebes dan satu product tidak memiliki name
products.drop(indexData , inplace=True)

datetime_column = ["order_purchase_timestamp","order_approved_at","order_delivered_carrier_date","order_delivered_customer_date","order_estimated_delivery_date"]
for i in datetime_column:
  orders[i] = pd.to_datetime(orders[i])

order_items["shipping_limit_date"] = pd.to_datetime(order_items["shipping_limit_date"])

# Impute order datetime
def impute_order_datetime(x,y):
    # x = target
    # y = patokan data yang membantu mencari selisih

    # Kita ambil data yang mau dihitung selisihnya untuk dicari rata-ratanya
    data = orders[[y,x]]
    # Hapus data yang kosong karena tidak bisa dihitung selisihnya
    data.dropna(inplace=True)

    # Kita cari selisihnya dan buat kolom baru bernama "time"
    time = data[x] - data[y]
    time = time.apply(lambda x: x.total_seconds())
    data["time"] = time

    # Cari rata-ratanya
    mean = round(data.time.mean())

    # Data x yang kosong kita isi dengan data y +
    for i, j in orders.iterrows():
        if pd.isna(j[x]):
            orders.at[i,x] = orders.at[i,y] + pd.to_timedelta(mean, unit='s')

impute_order_datetime("order_approved_at","order_purchase_timestamp")
impute_order_datetime("order_delivered_carrier_date","order_approved_at")
impute_order_datetime("order_delivered_customer_date","order_delivered_carrier_date")

# Impute review
order_reviews["review_comment_title"].fillna("No title", inplace = True)
order_reviews["review_comment_message"].fillna("No comment", inplace = True)

# Impute product
products["product_category_name"].fillna("unknown", inplace = True)
products["product_name_lenght"].fillna(round(products["product_name_lenght"].mean()), inplace = True)
products["product_description_lenght"].fillna(round(products["product_description_lenght"].mean()), inplace = True)
products["product_photos_qty"].fillna(products["product_photos_qty"].mode()[0], inplace = True)

# Ternyata ada yang memiliki berat 0
cama = products[products.product_category_name == "cama_mesa_banho"]
# Kita hilangkan yang 0 agar tidak mengganggu saat mengambil rata-rata
cama = cama[cama.product_weight_g > 0]
products["product_weight_g"] = products["product_weight_g"].apply(lambda x: round(cama["product_weight_g"].mean()) if x == 0 else x)

# hapus data yang tidak memiliki tipe pembayaran
indexData = order_payments[order_payments.payment_type == "not_defined"].index
order_payments.drop(indexData , inplace=True)

# Ganti underscore jadi spasi
products["product_category_name"] = products["product_category_name"].map(lambda x: " ".join(x.split("_")))
order_payments["payment_type"] = order_payments["payment_type"].map(lambda x: " ".join(x.split("_")))

# Dari hasil plot global kita lihat bahwa ada data yang outliers dan kita harus menghapusnya
indexGeoOut = geolocation.query("geolocation_lng > -30 or geolocation_lat > 10").index
geolocation.drop(index=indexGeoOut, inplace=True)
# Dari hasil plot lebih dekat kita lihat bahwa ada data yang berada di air, jadi kita harus menghapusnya
indexGeoOut = geolocation.query("(geolocation_lng < -58 and geolocation_lat < -30) or geolocation_lng > -33").index
geolocation.drop(index=indexGeoOut, inplace=True)

# UPDATE DATA
for i in range(len(table)):
  table[i].to_csv(f"../data/{table_name[i]}_dataset.csv")