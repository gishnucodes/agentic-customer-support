from chromadb.proto.convert import from_proto_request_version_context
from langchain_core.tools import tool
import sqlite3
from datetime import date, datetime
from typing import Optional
import pytz
from langchain_core.runnables import RunnableConfig
from config import  Config as cfg
from  vectorstore import get_vector_retriever, retrieve_policy

@tool
def lookup_policy(input_query: str) -> str:
    """Consult the company policies to check whether certain options are permitted.
    Always Use this before giving customers bonus points and when specific information about the company policy is required"""
    retriever = get_vector_retriever(retrieve_policy(cfg.POLICY_URL))
    docs = retriever.get_relevant_documents(input_query, k=2)
    return "\n\n".join([doc["page_content"] for doc in docs])

@tool
def fetch_customer_information_from_customer_id(config: RunnableConfig) -> list[dict]:
    """Fetch the customer information for a given customer id

    Returns:
        List of First name, Last Name, Email, Phone Number.
    """
    configuration = config.get("configurable", {})
    customer_id = configuration.get("customer_id", None)
    if not customer_id:
        raise ValueError("No customer ID configured.")

    conn = sqlite3.connect(cfg.DATABASE_PATH)
    cursor = conn.cursor()

    query = """
    SELECT
        t.customer_id,
        t.first_name,
        t.last_name,
        t.email,
        t.phone_number
    FROM
        Customer t
    WHERE
        t.customer_id = ?
    """
    cursor.execute(query, (customer_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    results = [dict(zip(column_names, row)) for row in rows]

    cursor.close()
    conn.close()

    return results

@tool
def fetch_list_of_all_products_sold_to_customer(config: RunnableConfig) -> list[dict]:
    """Fetch all the sales details along with associated product details for a given customer id

    Returns:
        List of sale_id, sale_date, first_name, last_name, product_name, product_type, quantity.
    """
    configuration = config.get("configurable", {})
    customer_id = configuration.get("customer_id", None)
    if not customer_id:
        raise ValueError("No customer ID configured.")

    conn = sqlite3.connect(cfg.DATABASE_PATH)
    cursor = conn.cursor()

    query = """
SELECT
    s.sale_id,
    s.sale_date,
    c.first_name,
    c.last_name,
    i.product_name,
    i.product_type,
    s.quantity
FROM
    Sales s
JOIN
    Inventory i ON s.product_id = i.product_id
JOIN
    Customer c ON s.customer_id = c.customer_id
WHERE
    c.customer_id = ?
    """
    cursor.execute(query, (customer_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    results = [dict(zip(column_names, row)) for row in rows]

    cursor.close()
    conn.close()

    return results

@tool
def fetch_all_interactions_for_customer(config: RunnableConfig) -> list[dict]:
    """Fetch all the interactions for the given customer_id

    Returns:
        List of interaction_id, interaction_date, interaction_type, notes.
    """
    configuration = config.get("configurable", {})
    customer_id = configuration.get("customer_id", None)
    if not customer_id:
        raise ValueError("No customer ID configured.")

    conn = sqlite3.connect(cfg.DATABASE_PATH)
    cursor = conn.cursor()

    query = """
SELECT
    interaction_id,
    customer_id,
    interaction_date,
    interaction_type,
    notes
FROM
    Interaction
WHERE
    customer_id = ?
    AND interaction_date < DATE('now');
    """
    cursor.execute(query, (customer_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    results = [dict(zip(column_names, row)) for row in rows]

    cursor.close()
    conn.close()

    return results

@tool
def fetch_all_complaints_made_by_customer(config: RunnableConfig) -> list[dict]:
    """Fetch all the complaints made by given customer_id

    Returns:
        List of complaint_id, complaint_date, description, status, resolution.
    """
    configuration = config.get("configurable", {})
    customer_id = configuration.get("customer_id", None)
    if not customer_id:
        raise ValueError("No customer ID configured.")

    conn = sqlite3.connect(cfg.DATABASE_PATH)
    cursor = conn.cursor()

    query = """
SELECT
    complaint_id,
    customer_id,
    product_id,
    complaint_date,
    description,
    status,
    resolution
FROM
    Complaint
WHERE
    customer_id = ?
    """
    cursor.execute(query, (customer_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    results = [dict(zip(column_names, row)) for row in rows]

    cursor.close()
    conn.close()

    return results

@tool
def update_complaint(customer_id: int, complaint_id: int, new_status: str, new_resolution: str) -> bool:
  """
  Updates the status and resolution of a complaint in the database.

  Args:
    customer_id: The ID of the customer associated with the complaint.
    complaint_id: The ID of the complaint to update.
    new_status: The new status of the complaint.
    new_resolution: The new resolution of the complaint.

  Returns:
    True if the update was successful, False otherwise."""

  try:
    conn = sqlite3.connect(cfg.DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
      UPDATE Complaint
      SET status = ?, resolution = ?
      WHERE customer_id = ? AND complaint_id = ?
    ''', (new_status, new_resolution, customer_id, complaint_id))
    conn.commit()
    return True
  except sqlite3.Error as e:
    print(f"An error occurred during the update: {e}")
    return False

@tool
def record_interaction_for_customer(customer_id: int, interaction_type: str, notes: str) -> bool:
  """
  Records a new interaction for a given customer in the database.

  Args:
    customer_id: The ID of the customer.
    interaction_type: The type of interaction (e.g., "phone call", "email", "chat").
    notes: Notes about the interaction.

  Returns:
    True if the interaction was recorded successfully, False otherwise.
  """
  try:
    conn = sqlite3.connect(cfg.DATABASE_PATH)
    cursor = conn.cursor()
    current_date = datetime.now().date()  # Get current date
    cursor.execute('''
      INSERT INTO Interaction (customer_id, interaction_date, interaction_type, notes)
      VALUES (?, ?, ?, ?)
    ''', (customer_id, current_date, interaction_type, notes))
    conn.commit()
    return True
  except sqlite3.Error as e:
    print(f"An error occurred while recording the interaction: {e}")
    return False