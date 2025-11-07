from utils.db import run_query

def get_analytics_data():
    """Collect summarized analytics for the dashboard-like analytics page."""
    # Average pet age per shelter
    avg_age = run_query("""
        SELECT s.name AS shelter_name, ROUND(AVG(p.age),2) AS avg_age
        FROM Pet p
        JOIN Shelter s ON p.shelter_id = s.shelter_id
        GROUP BY s.shelter_id;
    """, fetch=True)

    # Total adoptions by user
    adoptions_by_user = run_query("""
        SELECT u.name AS user_name, COUNT(a.adopt_app_id) AS total_adoptions
        FROM AdoptionApplication a
        JOIN User u ON a.user_id = u.user_id
        WHERE a.status = 'Approved'
        GROUP BY u.user_id
        ORDER BY total_adoptions DESC
        LIMIT 5;
    """, fetch=True)

    # Payment stats (sum per method)
    payments = run_query("""
        SELECT method, SUM(amount) AS total
        FROM Payment
        WHERE status = 'Completed'
        GROUP BY method;
    """, fetch=True)

    # Pet count per status
    pet_status = run_query("""
        SELECT status, COUNT(*) AS total
        FROM Pet
        GROUP BY status;
    """, fetch=True)

    return {
        "avg_age_data": {
            "labels": [row["shelter_name"] for row in avg_age],
            "values": [row["avg_age"] for row in avg_age]
        },
        "adoptions_by_user": {
            "labels": [row["user_name"] for row in adoptions_by_user],
            "values": [row["total_adoptions"] for row in adoptions_by_user]
        },
        "payment_data": {
            "labels": [row["method"] for row in payments],
            "values": [float(row["total"]) for row in payments]
        },
        "pet_status_data": {
            "labels": [row["status"] for row in pet_status],
            "values": [row["total"] for row in pet_status]
        }
    }
