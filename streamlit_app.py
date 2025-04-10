import streamlit as st
import json
import io

st.set_page_config(page_title="Blood Logistics Tool Input", layout="wide")

st.title("ONR Blood Management Support Tool")
st.sidebar.header("User Input")

# Ensure session state for user data
if "user_data" not in st.session_state:
    st.session_state.user_data = []

# Create the form
with st.form("blood_management_form"):
    simulation_days = st.number_input("Length of Simulation in Days:", min_value=0)
    med_log_company = st.number_input("Medical Logistics Company ID:", min_value=0)
    blood_inventory = st.number_input("Fresh Whole Blood Inventory on Hand (pints):", min_value=0)

    # Transportation Schedule Section
    st.markdown("### Transportation Schedule")

    transport_frequency = st.selectbox("Select Frequency:", options=[
        "Daily", "Weekly", "Bi-weekly", "Monthly", "Other"
    ])

    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    selected_days = st.multiselect("Select Delivery Days:", days_of_week, key="delivery_days")

    pickup_time = st.time_input("Pickup Time (24hr):")
    dropoff_time = st.time_input("Drop-off Time (24hr):")
    transport_capacity = st.number_input("Transportation Capacity (pints per trip):", min_value=0)

    # Number of platoons
    num_med_platoons = st.number_input("Number of Medical Platoons:", min_value=0, step=1)

    # Dynamic inputs for each platoon
    platoon_data = []
    for i in range(int(num_med_platoons)):
        st.markdown(f"### Platoon {i + 1}")
        platoon_id = st.number_input(f"Enter ID for Platoon {i + 1}:", format="%d", step=1, min_value=0, key=f"platoon_id_{i}")
        platoon_size = st.number_input(f"Enter Size (people) for Platoon {i + 1}:", min_value=0, key=f"platoon_size_{i}")
        delivery_time = st.time_input(f"Expected Delivery Time for Platoon {i + 1}:", key=f"delivery_time_{i}")
        conflict_likelihood = st.slider(
            f"Likelihood of Conflict Tomorrow (0–5) for Platoon {i + 1}:",
            min_value=0, max_value=5, value=0, step=1, key=f"conflict_{i}"
        )
        platoon_data.append({
            "Platoon ID": int(platoon_id),
            "Platoon Size": platoon_size,
            "Expected Delivery Time": delivery_time.strftime("%H:%M"),
            "Conflict Likelihood": conflict_likelihood
        })

    submit = st.form_submit_button("Submit")

# Process form submission
if submit:
    # Validations
    if dropoff_time <= pickup_time:
        st.error("Drop-off time must be after pickup time.")
    elif transport_frequency == "Weekly" and len(selected_days) != 1:
        st.error("Please select exactly one delivery day for weekly frequency.")
    elif transport_frequency == "Bi-weekly" and len(selected_days) != 2:
        st.error("Please select exactly two delivery days for bi-weekly frequency.")
    elif len(selected_days) == 0:
        st.error("Please select at least one delivery day.")
    elif all(x is not None for x in [simulation_days, med_log_company, blood_inventory, transport_capacity]) and all(
        p["Platoon ID"] is not None and
        p["Platoon Size"] is not None and
        p["Expected Delivery Time"] is not None and
        p["Conflict Likelihood"] is not None
        for p in platoon_data):

        new_entry = {
            "Length of Simulation in Days": simulation_days,
            "Medical Logistics Company": med_log_company,
            "Fresh Whole Blood Inventory on Hand (pints)": blood_inventory,
            "Transportation Schedule": {
                "Frequency": transport_frequency,
                "Delivery Days": selected_days,
                "Pickup Time": pickup_time.strftime("%H:%M"),
                "Drop-off Time": dropoff_time.strftime("%H:%M"),
                "Capacity (pints per trip)": transport_capacity
            },
            "Number of Medical Platoons": num_med_platoons,
            "Platoons": platoon_data
        }
        st.session_state.user_data.append(new_entry)
        st.success("Data added successfully!")
    else:
        st.error("Please fill in all fields completely.")

# Display stored data
st.subheader("Stored User Data")
if st.session_state.user_data:
    st.json(st.session_state.user_data)

    # Convert data to JSON and provide a download link
    json_data = json.dumps(st.session_state.user_data, indent=4)
    json_file = io.BytesIO(json_data.encode())

    st.download_button(
        label="Download JSON File",
        data=json_file,
        file_name="user_data.json",
        mime="application/json"
    )
