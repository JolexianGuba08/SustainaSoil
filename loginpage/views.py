import bcrypt
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from google.cloud.firestore_v1 import FieldFilter

from loginpage.forms import LoginForm, SignUpPageForm, OTPVerificationForm
from homepage.models import Account
from loginpage.otp_verification import *


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
                                return redirect('homepage')
                            elif account.acc_type == 0:
                                # Account is customer
                                messages.success(request, 'Supplier successfully deleted.')
                                request.session['session_email'] = acc_email
                                request.session['session_user_id'] = account.acc_id
                                request.session['session_user_type'] = account.acc_type
                                print('Customer login')
                                return redirect('homepage')
                        elif account.acc_status == 2:
                            print('Error: This account has been removed and is no longer accessible.')
                            return redirect('login_page')
                        else:
                            print('Incorrect Email or Password: Please verify and try again.')
                            return redirect('login_page')
                    else:
                        print('Incorrect Email or Password: Please verify and try again.')
                        return redirect('login_page')

                except ObjectDoesNotExist:
                    print('Account not found')
                    return redirect('login_page')

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return redirect('login_page')
    return render(request, 'login.html', {'form': LoginForm()})


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
                .where('token', '==', token) \
                .where('email', '==', email) \
                .where('otp', '==', otp) \
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


def logout_page(request):
    del request.session['session_email']
    del request.session['session_user_id']
    del request.session['session_user_type']

    return redirect('login_page')
