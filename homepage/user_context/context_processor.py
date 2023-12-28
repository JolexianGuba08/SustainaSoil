from homepage.models import Account


def user_context(request):
    if 'session_email' in request.session and 'session_user_id' in request.session and 'session_user_type' in request.session:
        user_email = request.session.get('session_email')

        # Get the user object from account model using email
        user = Account.objects.get(acc_email=user_email)

        user_name = user.acc_first_name + ' ' + user.acc_last_name
        user_profile_pic = user.acc_profile_img
        user_background_img = user.acc_background_img
        first_name = user.acc_first_name
        last_name = user.acc_last_name
        phone = user.acc_phone
        acc_created_date = user.acc_date_added
        # format the date to dd/mm/yyyy
        acc_created_date = acc_created_date.strftime("%d/%m/%Y")

        context = {
            'user_email': user_email,
            'name': user_name.upper(),
            'background_img': user_background_img,
            'user_profile_pic': user_profile_pic,
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'acc_created_date': acc_created_date
        }
        return context
    else:
        context = {}
        return context
