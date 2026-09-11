import mysql.connector
import os
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306))
    )

def predict_issues():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT issue_type, location_id
        FROM complaints
    """)

    complaints = cursor.fetchall()

    cursor.close()
    conn.close()

    if not complaints:
        return {
            "status": "success",
            "message": "No complaint data available"
        }

    issue_counts = Counter(
        complaint["issue_type"]
        for complaint in complaints
    )

    location_counts = Counter(
        complaint["location_id"]
        for complaint in complaints
    )

    most_common_issue = issue_counts.most_common(1)[0]
    high_risk_location = location_counts.most_common(1)[0]

    return {
        "status": "success",
        "prediction": {
            "most_likely_issue": most_common_issue[0],
            "issue_count": most_common_issue[1],
            "high_risk_location_id": high_risk_location[0],
            "complaint_count": high_risk_location[1]
        }
    }

if __name__ == "__main__":
    print(predict_issues())