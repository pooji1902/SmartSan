from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306))
    )


# ---------------- HOME ----------------

@app.route("/")
def home():
    return jsonify({
        "message": "SmartSan Backend is Running"
    })


# ---------------- DATABASE TEST ----------------

@app.route("/api/db-test")
def db_test():

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT DATABASE()")
        database = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "database": database,
            "message": "MySQL connected successfully"
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ---------------- LOCATIONS ----------------

@app.route("/api/locations")
def get_locations():

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM locations")

        locations = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(locations)

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ---------------- CREATE COMPLAINT ----------------

@app.route("/api/complaints", methods=["POST"])
def create_complaint():

    try:

        data = request.get_json()

        location_id = data.get("location_id")
        issue_type = data.get("issue_type")
        source = data.get("source", "QR")
        priority = data.get("priority", "MEDIUM")
        details = data.get("details", "")

        if not location_id or not issue_type:

            return jsonify({
                "status": "error",
                "message": "Location and issue type are required"
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO complaints
        (location_id, issue_type, source, priority, status, details)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            location_id,
            issue_type,
            source,
            priority,
            "Pending",
            details
        )

        cursor.execute(query, values)

        conn.commit()

        complaint_id = cursor.lastrowid

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Complaint submitted successfully",
            "complaint_id": complaint_id
        }), 201

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ---------------- GET ALL COMPLAINTS ----------------

@app.route("/api/complaints", methods=["GET"])
def get_complaints():

    try:

        conn = get_db_connection()

        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT
            c.complaint_id,
            c.location_id,
            l.location_name,
            c.issue_type,
            c.source,
            c.priority,
            c.status,
            c.details,
            c.reported_at,
            c.resolved_at
        FROM complaints c
        LEFT JOIN locations l
        ON c.location_id = l.location_id
        ORDER BY c.reported_at DESC
        """

        cursor.execute(query)

        complaints = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(complaints)

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ---------------- UPDATE COMPLAINT STATUS ----------------

@app.route("/api/complaints/<int:complaint_id>/status", methods=["PUT"])
def update_status(complaint_id):

    try:

        data = request.get_json()

        status = data.get("status")

        allowed_status = [
            "Pending",
            "In Progress",
            "Resolved"
        ]

        if status not in allowed_status:

            return jsonify({
                "status": "error",
                "message": "Invalid status"
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        if status == "Resolved":

            query = """
            UPDATE complaints
            SET status = %s,
                resolved_at = CURRENT_TIMESTAMP
            WHERE complaint_id = %s
            """

            cursor.execute(
                query,
                (status, complaint_id)
            )

        else:

            query = """
            UPDATE complaints
            SET status = %s
            WHERE complaint_id = %s
            """

            cursor.execute(
                query,
                (status, complaint_id)
            )

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Complaint status updated successfully"
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ---------------- RUN SERVER ----------------
# ---------------- SENSOR DATA ----------------

@app.route("/api/sensor-data", methods=["POST"])
def receive_sensor_data():

    try:
        data = request.get_json()

        location_id = data.get("location_id")
        dustbin_level = data.get("dustbin_level", 0)
        soap_level = data.get("soap_level", 0)
        tissue_level = data.get("tissue_level", 0)
        leakage = data.get("leakage", False)
        air_quality = data.get("air_quality", "Normal")

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO sensor_data
        (location_id, dustbin_level, soap_level, tissue_level,
         leakage, air_quality)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            location_id,
            dustbin_level,
            soap_level,
            tissue_level,
            leakage,
            air_quality
        ))

        conn.commit()

        # Automatic dustbin alert
        if dustbin_level >= 80:

            cursor.execute("""
                INSERT INTO complaints
                (location_id, issue_type, source, priority, status, details)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                location_id,
                "Dustbin Full",
                "Sensor",
                "HIGH",
                "Pending",
                "Dustbin automatically detected as full by ESP32"
            ))

            conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Sensor data received successfully"
        }), 201

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
if __name__ == "__main__":
    app.run(debug=True)