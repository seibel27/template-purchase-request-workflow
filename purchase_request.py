from abstra.compat import use_legacy_threads
"""
Calling the use_legacy_threads function allows using
the legacy threads in versions > 3.0.0
https://abstra.io/docs/guides/use-legacy-threads/

The new way of using workflows is with tasks. Learn more
at https://abstra.io/docs/concepts/tasks/ and contact us
on any issues during your migration
"""
use_legacy_threads("forms")

from abstra.forms import *
from abstra.workflows import *
from abstra.tables import *
import os

finance_email = os.getenv("FINANCE_TEAM_EMAIL")
manager_email = os.getenv("MANAGER_EMAIL")

# gets the email owner information on the tables team


def team_info_by_email(email):

    stm = select_one("team", where={"company_email": email})
    print(stm)
    try:
        return stm
    except:
        display(
            "It appears that you're not registered in our database. Please get in touch with admin@example.com.")


# verify if the requester is a valid user
set_title("Purchase Request")
user = get_user()
requester_email = user.email

# builds the purchase request page
purchase_request = Page().display("Purchase Request", size="large")\
                         .read("Product/Service Description", key="description")\
                         .read_currency("Amount", key="amount", currency="USD")\
                         .read_number("Quantity", key="quantity", initial_value=1)\
                         .read_date("Receiving Deadline", key="deadline")\
                         .read_textarea("Reason for Purchase", key="reason")\
                         .run("Send Request")

description, amount, quantity, deadline, reason = purchase_request.values()

team_info = team_info_by_email(requester_email)
requester_team_id, requester_team_name, requester_team_position = team_info[
    "id"], team_info["name"], team_info["position"]

total_amount = amount * quantity

# sets the purchase request status based on the total amount and define the people to approve it
if total_amount <= 1000:
    purchase_request_status = "approved"
    assignee_emails = [finance_email]
elif 1000 < total_amount <= 5000:
    purchase_request_status = "pending_finance"
    assignee_emails = [finance_email]
else:
    purchase_request_status = "pending_manager"
    assignee_emails = [manager_email, finance_email]

# save the purchase request on the tables and send it to the approval process
purchase_request_id = insert("purchase_requests", {})["id"]
approvals = []
for approval_email in assignee_emails:
    team_approver_id = team_info_by_email(approval_email)["id"]
    purchase_request_approval = insert("purchase_request_approvals", {
        "purchase_request_id": purchase_request_id, "team_id": team_approver_id})
    purchase_request_approval["email"] = approval_email
    approvals.append(purchase_request_approval)


purchase_data = {"description": description, "amount": amount, "quantity": quantity,
                 "reason": reason, "deadline": deadline.isoformat(), "requester_intern_email": requester_email,
                 "requester_team_name": requester_team_name, "requester_team_id": requester_team_id,
                 "requester_team_position": requester_team_position, "purchase_request_id": purchase_request_id}

set_data("purchase_request_status", purchase_request_status)
set_data("assignee_emails", assignee_emails)
set_data("purchase_data", purchase_data)
