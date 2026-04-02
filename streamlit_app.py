import streamlit as st
import pickle
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- LOGIN SYSTEM ----------------
def login():
    st.title("🔐 Login Page")
    st.markdown("### 🛒 Retail Analytics System")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state["logged_in"] = True
            st.success("✅ Login Successful")
            st.rerun()
        else:
            st.error("❌ Invalid Username or Password")

# Session init
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()

# ---------------- LOGOUT ----------------
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout"):
    st.session_state["logged_in"] = False
    st.rerun()

# ---------------- BACKGROUND STYLE ----------------
def add_bg():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://images.unsplash.com/photo-1607083206968-13611e3d76db");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }

        .stApp::before {
            content: "";
            position: fixed;
            top: 0; left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.65);
            z-index: -1;
        }

        h1, h2, h3, h4, h5, h6, p, label {
            color: white !important;
        }

        .stButton>button {
            background-color: #ff4b4b;
            color: white;
            border-radius: 10px;
            height: 45px;
            width: 100%;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg()

# ---------------- LOAD MODEL ----------------
model = pickle.load(open("model/model.pkl", "rb"))

# ---------------- LOAD DATA ----------------
data = pd.read_csv("data/sales.csv")
data['Date'] = pd.to_datetime(data['Date'])

# ---------------- SIDEBAR ----------------
st.sidebar.title("📊 Dashboard Menu")

page = st.sidebar.radio("Go to", [
    "🏠 Overview",
    "📈 Sales Analytics",
    "🔮 Prediction",
    "🧠 Insights"
])

# ---------------- OVERVIEW ----------------
if page == "🏠 Overview":
    st.title("📊 Business Dashboard Overview")

    total_sales = data['Sales'].sum()
    avg_sales = data['Sales'].mean()
    total_customers = data['Customers'].sum()
    total_stores = data['Store'].nunique()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Total Sales", f"₹ {total_sales:,.0f}")
    col2.metric("📊 Avg Sales", f"₹ {avg_sales:,.0f}")
    col3.metric("👥 Customers", total_customers)
    col4.metric("🏬 Stores", total_stores)

# ---------------- ANALYTICS ----------------
elif page == "📈 Sales Analytics":
    st.title("📈 Sales Analytics")

    st.subheader("📅 Sales Trend")
    fig, ax = plt.subplots()
    ax.plot(data['Date'], data['Sales'])
    st.pyplot(fig)

    st.subheader("🏬 Store-wise Sales")
    store_sales = data.groupby('Store')['Sales'].sum()
    fig2, ax2 = plt.subplots()
    store_sales.plot(kind='bar', ax=ax2)
    st.pyplot(fig2)

    # -------- FUTURE FORECAST --------
    st.subheader("📉 Future Forecast")

    data['DayIndex'] = range(len(data))

    from sklearn.linear_model import LinearRegression
    model_lr = LinearRegression()

    X = data[['DayIndex']]
    y = data['Sales']

    model_lr.fit(X, y)

    future = pd.DataFrame({'DayIndex': range(len(data), len(data)+30)})
    pred = model_lr.predict(future)

    fig3, ax3 = plt.subplots()
    ax3.plot(data['DayIndex'], y, label="Actual")
    ax3.plot(future['DayIndex'], pred, label="Forecast")
    ax3.legend()
    st.pyplot(fig3)

# ---------------- PREDICTION ----------------
elif page == "🔮 Prediction":
    st.title("🔮 Sales Prediction")

    store = st.number_input("Store ID", 1)

    product = st.selectbox("Product", ["A", "B"])
    product_map = {"A": 0, "B": 1}
    product_val = product_map[product]

    customers = st.number_input("Customers", 200)
    promo = st.selectbox("Promo", [0, 1])
    holiday = st.selectbox("Holiday", [0, 1])
    day = st.slider("Day", 1, 31)
    month = st.slider("Month", 1, 12)
    year = st.number_input("Year", 2023)

    input_data = {
        "Store": store,
        "Product": product_val,
        "Customers": customers,
        "Promo": promo,
        "Holiday": holiday,
        "Day": day,
        "Month": month,
        "Year": year
    }

    df = pd.DataFrame([input_data])

    if st.button("Predict Sales"):
        result = model.predict(df)
        st.success(f"💰 Predicted Sales: ₹ {result[0]:,.2f}")

        fig4, ax4 = plt.subplots()
        ax4.bar(["Predicted"], [result[0]])
        st.pyplot(fig4)

# ---------------- INSIGHTS ----------------
elif page == "🧠 Insights":
    st.title("🧠 Business Insights")

    best_store = data.groupby('Store')['Sales'].sum().idxmax()
    best_day = data.groupby(data['Date'].dt.day_name())['Sales'].sum().idxmax()

    st.success(f"🏆 Best Performing Store: {best_store}")
    st.success(f"📅 Best Sales Day: {best_day}")

    promo_impact = data.groupby('Promo')['Sales'].mean()

    fig5, ax5 = plt.subplots()
    promo_impact.plot(kind='bar', ax=ax5)
    st.pyplot(fig5)

    # -------- CHATBOT --------
    st.subheader("🤖 AI Chatbot")

    query = st.text_input("Ask about business")

    if query:
        query = query.lower()

        if "best store" in query:
            best = data.groupby('Store')['Sales'].sum().idxmax()
            st.success(f"🏆 Best Store: {best}")

        elif "worst store" in query:
            worst = data.groupby('Store')['Sales'].sum().idxmin()
            st.warning(f"📉 Worst Store: {worst}")

        elif "total sales" in query:
            st.info(f"💰 Total Sales: ₹ {data['Sales'].sum():,.0f}")

        elif "customers" in query:
            st.info(f"👥 Total Customers: {data['Customers'].sum()}")

        else:
            st.warning("Try: best store / total sales / customers")
