Based on the provided URLs from your Django application, here is a list of how to access each page on the frontend, assuming your Django server is running locally and set to the default port (8000). Please replace "localhost:8000" with the appropriate domain and port if your configuration is different.

### Core App URLs

1. **User Profile Settings:**

   - URL: `http://localhost:8000/core/account/user_profile_settings/`

2. **List Time Entries:**

   - URL: `http://localhost:8000/core/entries/`

3. **Clock In:**

   - URL: `http://localhost:8000/core/clock-in/`

4. **Clock Out:**

   - URL: `http://localhost:8000/core/clock-out/`

5. **Employee Dashboard:**

   - URL: `http://localhost:8000/core/employee_dashboard/`

6. **Apply Employer:**
   - URL: `http://localhost:8000/core/apply-employer/`

### Project-level (Time Tracker) URLs

1. **Admin:**

   - URL: `http://localhost:8000/admin/`

2. **User Registration:**

   - URL: `http://localhost:8000/register/`

3. **User Login:**

   - URL: `http://localhost:8000/accounts/login/`

4. **User Logout:**

   - URL: `http://localhost:8000/accounts/logout/`

5. **Password Change:**

   - URL: `http://localhost:8000/accounts/password_change/`

6. **Password Change Done:**

   - URL: `http://localhost:8000/accounts/password_change/done/`

7. **Password Reset:**

   - URL: `http://localhost:8000/accounts/password_reset/`

8. **Password Reset Done:**

   - URL: `http://localhost:8000/accounts/password_reset/done/`

9. **Password Reset Confirm:**

   - Use the link provided in the email sent during the reset process (dynamic URL).

10. **Password Reset Complete:**

- URL: `http://localhost:8000/accounts/reset/done/`

11. **Dashboard Redirect:**

- URL: `http://localhost:8000/dashboard_redirect/`

12. **Activate Account:**

    - Use the link provided in the activation email (dynamic URL).

13. **Account Activation Sent:**

- URL: `http://localhost:8000/account_activation_sent/`

14. **User Application Settings:**

- URL: `http://localhost:8000/user_app_settings/`

### Employer App URLs

1. **Register User (Employer):**

   - URL: `http://localhost:8000/employer/register/user/`

2. **Register Employer Details:**

   - URL: `http://localhost:8000/employer/register/details/`

3. **Employer Dashboard:**

   - URL: `http://localhost:8000/employer/employer_dashboard/`

4. **Invitation Sent (Employer):**

   - URL: `http://localhost:8000/employer/invitation/sent/`

5. **Send Invitation (Employer):**

   - URL: `http://localhost:8000/employer/invitation/send/`

6. **Accept Invitation (Employer):**

   - Use the link provided in the invitation email (dynamic URL).

7. **List Time Entries (Employer):**
   - URL: `http://localhost:8000/employer/list-time-entries/`

### Important Notes:

- Some URLs like password reset confirmation and account activation are dynamic and include tokens. Users typically access these through email links sent by the system.
- Ensure that the Django server is running and the app is properly configured to serve these routes.
- Replace "localhost:8000" with your actual domain and port if different.
- Make sure the user is appropriately authenticated and has the necessary permissions to access certain views, especially for operations like changing passwords, viewing the dashboard, etc.
- For any URLs under the 'accounts' path, Django's default auth views are used. Make sure `django.contrib.auth.urls` is included in your project-level `urls.py` (which you have done).
- Test each URL individually to ensure they are working as expected and that the views and templates are correctly set up to handle the requests.
