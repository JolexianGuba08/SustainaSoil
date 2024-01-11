import bcrypt
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from google.cloud.firestore_v1 import FieldFilter

from loginpage.forms import LoginForm, SignUpPageForm, OTPVerificationForm, ForgotPasswordForm, ChangePasswordForm
from homepage.models import Account
from loginpage.otp_verification import *
import homepage.firestore_db_modules.forgot_password_module as forgot_password_module


# Login page with session
def login_page(request):
    # check if there are any session variables from otp_verifications
    if 'redirect_token' in request.session and 'redirect_email' in request.session:
        del_session(request)

    # check if there are any session variables from login
    if 'session_email' in request.session and 'session_user_id' in request.session and 'session_user_type' in request.session:
        return redirect('homepage')

    # check if the request is a POST request
    if request.method == 'POST':
        form = LoginForm(request.POST)
        try:
            if form.is_valid():
                acc_email = form.cleaned_data['acc_email']
                acc_password = form.cleaned_data['acc_password']

                try:
                    account = Account.objects.get(acc_email=acc_email)

                    if bcrypt.checkpw(acc_password.encode('utf8'), account.acc_password.encode('utf8')):
                        if account.acc_status == 1:
                            if account.acc_type == 1:
                                # Account is an admin
                                print('Admin login')
                                # return redirect('homepage')
                            elif account.acc_type == 0:
                                # Account is customer

                                request.session['session_email'] = acc_email
                                request.session['session_user_id'] = account.acc_id
                                request.session['session_user_type'] = account.acc_type
                                print('Customer login')
                                # Assuming the login is successful, return a JSON response
                                dashboard_html = render_to_string('dashboard_page/user-dashboard.html')
                                return JsonResponse({'success': True, 'dashboard_html': dashboard_html})
                        elif account.acc_status == 2:
                            print('Error: This account has been removed and is no longer accessible.')
                            errors = 'Error: This account has been removed and is no longer accessible.'
                            return JsonResponse({'success': False, 'errors': errors})
                        else:
                            print('Incorrect Email or Password: Please verify and try again.')
                            errors = 'Incorrect Email or Password: Please verify and try again.'
                            return JsonResponse({'success': False, 'errors': errors})
                    else:
                        print('Incorrect Email or Password: Please verify and try again.')
                        errors = 'Incorrect Email or Password: Please verify and try again.'
                        return JsonResponse({'success': False, 'errors': errors})

                except ObjectDoesNotExist:
                    print('Account not found')
                    errors = 'Account not found'
                    return JsonResponse({'success': False, 'errors': errors})

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return redirect('login_page')
    return render(request, 'login.html', {'form': LoginForm()})


# Signup page with session
def signup_page(request):
    if 'redirect_token' in request.session and 'redirect_email' in request.session:
        del_session(request)
    if 'session_email' in request.session and 'session_user_id' in request.session and 'session_user_type' in request.session:
        return redirect('homepage')
    if request.method == 'POST':
        form = SignUpPageForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            email = cleaned_data['acc_email'].lower()
            acc_first_name = cleaned_data['acc_first_name']
            acc_last_name = cleaned_data['acc_last_name']
            acc_password = cleaned_data['acc_password']

            # Check if the account with the email already exists
            if Account.objects.filter(acc_email__iexact=email).exists():
                return render(request, 'signup.html', {'form': form, 'error_message': 'Email address already in use'})

            # Proceed to OTP verification
            token = generate_token()
            send_the_otp_to_database(email, token)
            request.session['redirect_email'] = email
            request.session['redirect_token'] = token
            request.session['redirect_first_name'] = acc_first_name
            request.session['redirect_last_name'] = acc_last_name
            request.session['redirect_password'] = acc_password

            return redirect('otp_verification')
        else:
            for field in form:
                if field.name in form.errors:
                    return render(request, 'signup.html', {'form': form, 'error_message': form.errors[field.name]})
            return render(request, 'signup.html', {'form': form})
    else:
        form = SignUpPageForm()
    return render(request, 'signup.html', {'form': form})


# OTP Verification
def otp_verification(request):
    if request.session.get('redirect_token') is None:
        return HttpResponse('403 Forbidden')

    email = request.session.get('redirect_email')
    token = request.session.get('redirect_token')
    first_name = request.session.get('redirect_first_name')
    last_name = request.session.get('redirect_last_name')
    password = request.session.get('redirect_password')
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            otp1 = cleaned_data['otp1']
            otp2 = cleaned_data['otp2']
            otp3 = cleaned_data['otp3']
            otp4 = cleaned_data['otp4']
            otp5 = cleaned_data['otp5']
            otp6 = cleaned_data['otp6']

            # Concatenate OTP
            otp = otp1 + otp2 + otp3 + otp4 + otp5 + otp6

            # Initialize Firestore client
            db = firestore_database()

            # Check if token, email, and OTP match in the database
            otp_verification_ref = db.collection('otp_verification') \
                .where(filter=FieldFilter('token', '==', token)) \
                .where(filter=FieldFilter('email', '==', email)) \
                .where(filter=FieldFilter('otp', '==', otp)) \
                .stream()

            found = False
            for _ in otp_verification_ref:
                # Token, email, and OTP match found in the database
                found = True
                break

            if found:
                # Valid OTP entered by the user
                # Perform actions for a successful OTP verification
                # For example, update user status, log them in, etc.
                print('OTP verified successfully!')

                # Create an Account object and save it to the database
                Account.objects.create(
                    acc_email=email,
                    acc_first_name=first_name,
                    acc_last_name=last_name,
                    acc_password=password
                )
                send_congrats_email(email)  # Send congratulatory email function
                # Optionally, clear the session variables after successful creation
                del request.session['redirect_email']
                del request.session['redirect_token']
                del request.session['redirect_first_name']
                del request.session['redirect_last_name']
                del request.session['redirect_password']

                return redirect('login_page')
            else:
                # Invalid OTP entered by the user
                print('Invalid OTP!')

        else:
            # Form is not valid
            print(form.errors)
    else:
        form = OTPVerificationForm()

    return render(request, 'otp_verification.html', {'form': form, 'email': email})


# Resend OTP Verification
def resend_otp(request):
    redirect_email = request.session.get('redirect_email')
    redirect_token = request.session.get('redirect_token')

    if redirect_email is None or redirect_token is None:
        return HttpResponse('403 Forbidden')

    # Initialize Firestore client
    db = firestore_database()

    otp_verification_ref = (
        # db.collection('otp_verification').where('token', '==', redirect_token).where('email', '==', redirect_email)
        db.collection('otp_verification').where(filter=FieldFilter('token', '==', redirect_token)).where(
            filter=FieldFilter('email', '==', redirect_email))
    )
    try:
        otp_verification_query = otp_verification_ref.get()

        if not otp_verification_query:
            return HttpResponse('Bad Request. Please try to Sign Up Again')
        otp = ''
        # Assuming the query returns only one document, retrieve the OTP
        for doc in otp_verification_query:
            otp = doc.to_dict().get('otp')
        send_otp_to_email(redirect_email, otp)  # Send OTP to email function
        return redirect('otp_verification')

    except Exception as e:
        print(f'Error in fetching the OTP Code: {e}')


# Logout page
def logout_page(request):
    if not request.session.get('session_email'):
        return redirect('login_page')
    del request.session['session_email']
    del request.session['session_user_id']
    del request.session['session_user_type']

    return redirect('login_page')


def forgot_password_page(request):
    form = ForgotPasswordForm(request.POST)
    return render(request, 'forgot_password.html', {'form': form})


# Change Password Page
def change_password_page(request, session_token):
    session_data = forgot_password_module.search_forgot_password_session(session_token)
    if session_data is None:
        return HttpResponse('403 Forbidden Token not Valid')
    expiration_date = ''
    expired = False
    for doc in session_data:
        email = doc.to_dict()['email']
        expiration_date = doc.to_dict()['expiration_date']
        expired = doc.to_dict()['expired']
        print(email)
    # check if the token is expired
    if datetime.now() > datetime.strptime(expiration_date, "%B %d, %Y at %I:%M:%S %p UTC+8"):
        print('Token is expired')
        return HttpResponse('403 Token is expired')
    if expired:
        print('Token is expired')
        return HttpResponse('403 Token is expired')
    # print remaining time in minutes
    remaining_time = datetime.strptime(expiration_date, "%B %d, %Y at %I:%M:%S %p UTC+8") - datetime.now()
    print(remaining_time.seconds / 60, 'minutes remaining')

    form = ChangePasswordForm(request.POST)
    return render(request, 'change_password.html', {'form': form})


def check_forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            email = cleaned_data['acc_email'].lower()
            try:
                account = Account.objects.get(acc_email=email)
                if account:
                    session_token = generate_token()
                    forgot_password_module.add_forgot_password_session(email, session_token)
                    send_link_change_password_to_email(email, session_token)
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False})
            except ObjectDoesNotExist:
                return JsonResponse({'success': False, 'errors': 'Account not found'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = ForgotPasswordForm()
    return render(request, 'forgot_password.html', {'form': form})


def change_forgot_password(request, session_token):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            password = cleaned_data['new_password']
            confirm_password = cleaned_data['confirm_password']
            session_search = forgot_password_module.search_forgot_password_session(session_token)
            if session_search is None:
                return HttpResponse('403 Forbidden Token not Valid')
            expiration_date = ''
            expired = False
            email = ''
            for doc in session_search:
                email = doc.to_dict()['email']
                expiration_date = doc.to_dict()['expiration_date']
                expired = doc.to_dict()['expired']
            # check if the token is expired
            if datetime.now() > datetime.strptime(expiration_date, "%B %d, %Y at %I:%M:%S %p UTC+8"):
                return JsonResponse({'success': False, 'errors': 'Token is expired'})
            if expired:
                return JsonResponse({'success': False, 'errors': 'Token is expired'})

            if password != confirm_password:
                return JsonResponse({'success': False, 'errors': 'Passwords do not match'})
            # validate password should be 8 characters long and should contain at least 1 uppercase, 1 lowercase, 1 number, and 1 special character
            if len(password) < 8:
                return JsonResponse({'success': False, 'errors': 'Password should be at least 8 characters long'})
            if not any(char.isdigit() for char in password):
                return JsonResponse({'success': False, 'errors': 'Password should contain at least 1 number'})
            if not any(char.isupper() for char in password):
                return JsonResponse({'success': False, 'errors': 'Password should contain at least 1 uppercase letter'})
            if not any(char.islower() for char in password):
                return JsonResponse({'success': False, 'errors': 'Password should contain at least 1 lowercase letter'})
            if not any(char in '!@#$%^&*()_+{}[]|:;<>,.?/~`' for char in password):
                return JsonResponse(
                    {'success': False, 'errors': 'Password should contain at least 1 special character'})
            # Update the Account password in the database
            account = Account.objects.get(acc_email=email)
            # check if password is the same as the old password
            if bcrypt.checkpw(password.encode('utf8'), account.acc_password.encode('utf8')):
                return JsonResponse(
                    {'success': False, 'errors': 'New password should be different from the old password'})
            account.acc_password = password
            account.save()
            # Update the Forgot Password Session to expired
            forgot_password_module.update_forgot_password_session(session_token)

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = ChangePasswordForm()
    return render(request, 'change_password.html', {'form': form})
