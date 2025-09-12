import cx_Oracle
try:
    conn = cx_Oracle.connect(user="C##gymadmin", password="gympassword", dsn="localhost:1521/XE")
    print("✅ Connected to CDB as C## user!")
    conn.close()
    
    conn = cx_Oracle.connect(user="gymadmin", password="gympassword", dsn="localhost:1521/XEPDB1")
    print("✅ Connected to PDB as local user!")
    conn.close()
except Exception as e:
    print("❌ Error:", e)