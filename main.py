import sqlite3
import streamlit as st

st.set_page_config(page_title="Visited Places Tracker", page_icon="🗺️", layout="wide")

conn = sqlite3.connect('visited_places1.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
          )''')

c.execute('''CREATE TABLE IF NOT EXISTS places (
            place_id INTEGER PRIMARY KEY AUTOINCREMENT,
            place_name TEXT NOT NULL,
            number_of_visits INTEGER DEFAULT 0
          )''')

c.execute('''CREATE TABLE IF NOT EXISTS visits (
            visit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            place_id INTEGER NOT NULL,
            visit_date TEXT NOT NULL,
            stay_duration INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (place_id) REFERENCES places (place_id)
          )''')

conn.commit()
def add_user(name):
    c.execute('INSERT INTO users (name) VALUES (?)', (name,))
    conn.commit()
    return c.lastrowid

def add_place(place_name):
    c.execute('INSERT INTO places (place_name) VALUES (?)', (place_name,))
    conn.commit()
    return c.lastrowid  

def log_visit(user_id, place_id, visit_date, stay_duration):
    c.execute('INSERT INTO visits (user_id, place_id, visit_date, stay_duration) VALUES (?, ?, ?, ?)', (user_id, place_id, visit_date, stay_duration))
    c.execute('UPDATE places SET number_of_visits = number_of_visits + 1 WHERE place_id = ?', (place_id,))
    conn.commit()

def get_user_visits(user_id):
    c.execute('''SELECT p.place_name, v.visit_date, v.stay_duration 
                 FROM visits v 
                 JOIN places p ON v.place_id = p.place_id 
                 WHERE v.user_id = ?''', (user_id,))
    return c.fetchall()

def get_most_visited_places():
    c.execute('SELECT place_name, number_of_visits FROM places ORDER BY number_of_visits DESC')
    return c.fetchall()

def update_user_name(user_id, new_name):
    c.execute('UPDATE users SET name = ? WHERE user_id = ?', (new_name, user_id))
    conn.commit()

def update_place(place_id, new_name, new_visit_count=None):
    if new_visit_count is not None:
        c.execute('UPDATE places SET place_name = ?, number_of_visits = ? WHERE place_id = ?', (new_name, new_visit_count, place_id))
    else:
        c.execute('UPDATE places SET place_name = ? WHERE place_id = ?', (new_name, place_id))
    conn.commit()

def delete_visit(visit_id):
    c.execute('DELETE FROM visits WHERE visit_id = ?', (visit_id,))
    conn.commit()

def delete_place(place_id):
    c.execute('DELETE FROM places WHERE place_id = ?', (place_id,))
    c.execute('DELETE FROM visits WHERE place_id = ?', (place_id,))
    conn.commit()

def delete_user(user_id):
    c.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
    c.execute('DELETE FROM visits WHERE user_id = ?', (user_id,))
    conn.commit()

def update_visit(visit_id, new_date=None, new_duration=None):
    if new_date and new_duration is not None:
        c.execute('UPDATE visits SET visit_date = ?, stay_duration = ? WHERE visit_id = ?', (new_date, new_duration, visit_id))
    elif new_date:
        c.execute('UPDATE visits SET visit_date = ? WHERE visit_id = ?', (new_date, visit_id))
    elif new_duration is not None:
        c.execute('UPDATE visits SET stay_duration = ? WHERE visit_id = ?', (new_duration, visit_id))
    conn.commit()

def get_users():
    c.execute('SELECT user_id, name FROM users ORDER BY name ASC')
    return c.fetchall()

def get_places_list():
    c.execute('SELECT place_id, place_name, number_of_visits FROM places ORDER BY place_name ASC')
    return c.fetchall()

def main():
    st.title("Visited Places Tracker")

    with st.sidebar:
        st.header("Navigation")
        menu = ["Add User", "Delete User", "Add Place", "Delete User", "Log Visit", "Delete Visit", "View Visits", "Most Visited Places"]
        choice = st.radio("Go to", menu, index=0)

        places = get_places_list()
        total_places = len(places)
        total_users = len(get_users())
        total_visits = sum(p[2] for p in places) if places else 0
        st.markdown("---")
        st.caption("Quick Stats")
        c1, c2, c3 = st.columns(3)
        c1.metric("Users", total_users)
        c2.metric("Places", total_places)
        c3.metric("Visits", total_visits)

    if choice == "Add User":
        st.subheader("Add New User")
        with st.form(key="form_add_user", clear_on_submit=True):
            name = st.text_input("User name", placeholder="Jane Doe")
            submitted = st.form_submit_button("Add User")
        if submitted:
            if name and name.strip():
                user_id = add_user(name.strip())
                st.success(f"User '{name}' added with ID {user_id}")
            else:
                st.error("Please enter a valid name.")
    
    elif choice == "Delete User":
        st.subheader("Delete User")
        users = get_users()
        if not users:
            st.info("No users found. Add a user first.")
        else:
            user_names = {f"{u[1]} (ID {u[0]})": u[0] for u in users}
            selected_user_label = st.selectbox("Select user to delete", list(user_names.keys()))
            if st.button("Delete User"):
                selected_user_id = user_names.get(selected_user_label)
                if selected_user_id:
                    delete_user(selected_user_id)
                    st.success(f"User '{selected_user_label.split(' (ID')[0]}' deleted.")
                else:
                    st.error("Please select a valid user.")

    elif choice == "Add Place":
        st.subheader("Add New Place")
        with st.form(key="form_add_place", clear_on_submit=True):
            place_name = st.text_input("Place name", placeholder="Central Park")
            submitted = st.form_submit_button("Add Place")
        if submitted:
            if place_name and place_name.strip():
                place_id = add_place(place_name.strip())
                st.success(f"Place '{place_name}' added with ID {place_id}")
            else:
                st.error("Please enter a valid place name.")

    elif choice == "Delete Place":
        st.subheader("Delete Place")
        places = get_places_list()
        if not places:
            st.info("No places found. Add a place first.")
        else:
            place_names = {f"{p[1]} (ID {p[0]})": p[0] for p in places}
            selected_place_label = st.selectbox("Select place to delete", list(place_names.keys()))
            if st.button("Delete Place"):
                selected_place_id = place_names.get(selected_place_label)
                if selected_place_id:
                    delete_place(selected_place_id)
                    st.success(f"Place '{selected_place_label.split(' (ID')[0]}' deleted.")
                else:
                    st.error("Please select a valid place.")

    elif choice == "Log Visit":
        st.subheader("Log a Visit")
        users = get_users()
        places = get_places_list()

        if not users or not places:
            st.info("You need at least one user and one place to log a visit.")
        else:
            user_names = {f"{u[1]} (ID {u[0]})": u[0] for u in users}
            place_names = {f"{p[1]} (ID {p[0]})": p[0] for p in places}

            with st.form(key="form_log_visit"):
                col1, col2 = st.columns(2)
                with col1:
                    selected_user_label = st.selectbox("User", list(user_names.keys()))
                with col2:
                    selected_place_label = st.selectbox("Place", list(place_names.keys()))

                col3, col4 = st.columns(2)
                with col3:
                    visit_date = st.date_input("Visit date")
                with col4:
                    stay_duration = st.number_input("Stay duration (minutes)", min_value=0, step=5)

                submitted = st.form_submit_button("Log Visit")

            if submitted:
                selected_user_id = user_names.get(selected_user_label)
                selected_place_id = place_names.get(selected_place_label)
                if selected_user_id and selected_place_id and visit_date and stay_duration >= 0:
                    log_visit(selected_user_id, selected_place_id, visit_date.isoformat(), int(stay_duration))
                    st.success(f"Visit logged for {selected_user_label.split(' (ID')[0]} at {selected_place_label.split(' (ID')[0]}")
                else:
                    st.error("Please fill in all fields correctly.")

    elif choice == "Delete Visit":
        st.subheader("Delete a Visit")
        users = get_users()
        if not users:
            st.info("No users found. Add a user first.")
        else:
            user_names = {f"{u[1]} (ID {u[0]})": u[0] for u in users}
            selected_user_label = st.selectbox("Select user", list(user_names.keys()))
            selected_user_id = user_names.get(selected_user_label)
            if selected_user_id:
                visits = get_user_visits(selected_user_id)
                if not visits:
                    st.info("No visits found for this user.")
                else:
                    visit_options = {f"{v[0]} on {v[1]} for {v[2]} min (Visit ID unknown)": idx for idx, v in enumerate(visits)}
                    selected_visit_label = st.selectbox("Select visit to delete", list(visit_options.keys()))
                    if st.button("Delete Visit"):
                        c.execute('''SELECT v.visit_id 
                                     FROM visits v 
                                     JOIN places p ON v.place_id = p.place_id 
                                     WHERE v.user_id = ? AND p.place_name = ? AND v.visit_date = ? AND v.stay_duration = ?''', 
                                  (selected_user_id, *selected_visit_label.split(' on ')[0:2], int(selected_visit_label.split(' for ')[1].split(' min')[0])))
                        visit_record = c.fetchone()
                        if visit_record:
                            delete_visit(visit_record[0])
                            st.success("Visit deleted.")
                        else:
                            st.error("Could not find the selected visit.")

    elif choice == "View Visits":
        st.subheader("View User Visits")
        users = get_users()
        if not users:
            st.info("No users found. Add a user first.")
        else:
            user_names = {f"{u[1]} (ID {u[0]})": u[0] for u in users}
            selected_user_label = st.selectbox("Select user", list(user_names.keys()))
            if st.button("Get Visits"):
                visits = get_user_visits(user_names[selected_user_label])
                if visits:
                    df_rows = [{"Place": v[0], "Date": v[1], "Duration (min)": v[2]} for v in visits]
                    st.dataframe(df_rows, use_container_width=True)
                else:
                    st.info("No visits found for this user.")

    elif choice == "Most Visited Places":
        st.subheader("Most Visited Places")
        places = get_most_visited_places()
        if places:
            top = places[:3]
            cols = st.columns(len(top))
            for idx, (name, count) in enumerate(top):
                cols[idx].metric(label=name, value=int(count))

            st.markdown("\n")
            table_rows = [{"Place": p[0], "Visits": p[1]} for p in places]
            st.dataframe(table_rows, use_container_width=True)
        else:
            st.info("No places found.")

if __name__ == "__main__":
    main()
    
